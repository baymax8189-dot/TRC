import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import psycopg2

# Get DB connection from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# Example function to save data to DB (customize as needed)
def save_to_db(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO stock_ticks (stock_name, symbol, links, percent_change, price, volume) VALUES (%s, %s, %s, %s, %s, %s)",
        data
    )
    conn.commit()
    cur.close()
    conn.close()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set the URL of the webpage you want to reload
url = "https://chartink.com/screener/15-minute-stock-breakouts"

# Set the stop time
stop_time = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)

driver = webdriver.Chrome(options=chrome_options)

try:
    while True:
        if datetime.now() > stop_time:
            print("Stopping execution as current time is past 3:30 PM.")
            break
        driver.get(url)
        # TODO: Add scraping logic here and call save_to_db(parsed_data)
        print("Page loaded. Implement scraping and DB save logic.")
        time.sleep(900)  # 15 minutes
finally:
    driver.quit()
