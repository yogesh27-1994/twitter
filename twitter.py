# For this code i am using selenium-stealth need to install with following command
# pip install selenium-stealth  

# import csv
from PIL import Image
import pytesseract
import re

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
import pymysql

# Setup Chrome options
options = Options()
options.add_argument("disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
options.add_argument("incognito")

# Initialize WebDriver
driver = webdriver.Chrome(options=options)

# Apply stealth settings
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# Open the target page
driver.get('https://x.com/wix')
driver.set_page_load_timeout(60)

# Wait for the page to fully load
time.sleep(10)

# Print page content
page_content = driver.page_source

# Take a screenshot as PNG
screenshot = driver.get_screenshot_as_png()

# Save the screenshot locally
with open('screenshot.png', 'wb') as file:
    file.write(screenshot)

print("Screenshot saved as 'screenshot.png'")
# Close the browser
driver.quit()
# Path to the image file
image_path = 'screenshot.png'

# Open the image using PIL
img = Image.open(image_path)
# Use pytesseract to extract text from the image
extracted_text = pytesseract.image_to_string(img)

if extracted_text:
    # Print the full extracted text (optional)
    print("Extracted Text:", extracted_text)
    cleaned_text = re.sub(r'[^a-zA-Z0-9@.,\'\s]', ' ', extracted_text)  # Remove special characters except '@', '.', etc.
    bio_text = re.sub(r'\s+', ' ', cleaned_text).strip()      # Replace multiple spaces/newlines with a single space and  Trim leading/trailing spaces
else:
    print("Bio not found")

# Extracting follower count using regex
followers_match = re.search(r'(\d+[.,]?\d*K?) Followers', extracted_text)
followers = followers_match.group(0) if followers_match else "Followers count not found"
# Displaying the results
print("Extracted Bio:", bio_text)
print("Extracted Follower Count:", followers)

## store data in csv file
# csv_filename = "twitter_data.csv"
# try:
#     with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file, quoting=csv.QUOTE_ALL)
#         # Write the header row
#         writer.writerow(["bio", "followers"])
#         # Write the data in separate columns
#         writer.writerow([bio_text, followers])
#     print(f"Data has been successfully saved to {csv_filename}")
# except IOError as e:
#     print(f"Error writing to CSV file: {e}")

# store data in MySql database
def connect_db():
    conn = pymysql.connect(
        host="127.1.0.0",
        port=3366,
        user="opt-root",
        password="root",
        db="twitter",
        autocommit=True,
    )
    return conn

connection = connect_db()
cursor = connection.cursor()

fields = [
        "bio_text",
        "followers"
    ]
fields = ",".join(fields)
values = [
    bio_text,
    followers
]

table = "twitter_data"
query = """
    INSERT INTO twitter_data (bio_text, followers) 
    VALUES (%s, %s)
"""
print(f"INSERT for {table} table## {query}")
cursor.execute(query,values)
id = cursor.lastrowid
print(id)
cursor.close()

