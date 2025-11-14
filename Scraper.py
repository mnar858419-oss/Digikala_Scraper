from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time


chrome_options = Options()
chrome_options.add_argument('--headless=new')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

product = input("Enter the name of the product: ")
product = product.replace(' ' , '')
url = f"https://www.digikala.com/search/?q={product}"
driver.get(url)

wait = WebDriverWait(driver, 10)

last_height = driver.execute_script("return document.body.scrollHeight")
SCROLL_PAUSE_TIME = 3.0

time.sleep(6)

try:
        
    button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='فعلا نه']]"))
    )
    
    button.click()
    
    time.sleep(1.5) 
    
except Exception as e:
    print("No Pop up window")


while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break 
    last_height = new_height

try:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="product-card"]')))
except:
    print("error")
    driver.quit()
    exit()

products = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-card"]')

data = []
for item in products:
    try:
        name = item.find_element(By.TAG_NAME, "h3")
        name = name.text.strip()

        try:
            price = item.find_element(By.CSS_SELECTOR, 'span[data-testid="price-final"]')
            price = price.text.strip()
        except :
            price = "ناموجود"

        data.append({"Name": name, "Price": price})
    except:
        print("error")
        

driver.quit()

# (تشکیل فایل CSV)
# -----------------------------------

filename = f'{product}.csv'
old_data = {}

if os.path.exists(filename):
    with open(filename, mode='r', newline='' , encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            price_number = int(row['Price'].replace(',', '').replace('٬', ''))
            old_data[row['Name']] = price_number

with open(filename, mode='w', newline='' , encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Price'])

    for item in data:
        if item['Price'] == "ناموجود":
            current_price = None 
        else:
            try:
                current_price = int(item['Price'].replace(',', '').replace('٬', ''))
            except ValueError:
                current_price = None

        if current_price is not None and item['Name'] in old_data:
            if current_price < old_data[item['Name']]:
                print(f"{item['Name']} : {old_data[item['Name']]} -> {current_price}")

        writer.writerow([item['Name'], item['Price']])

print(f"Done")
