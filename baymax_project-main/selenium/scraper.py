from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
import time
import os
from datetime import datetime
import logging
import sys

# Setup logging with file + console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration (EDIT THESE)
download_path = r"C:\Users\saikumar\Desktop\chartlink\15_minute"
os.makedirs(download_path, exist_ok=True)

API_URL = "https://chartlink-api.onrender.com"  # Replace with your Render URL
url = "https://chartink.com/screener/15-minute-stock-breakouts"

# Market hours: 9:15 AM to 3:30 PM (IST)
market_start = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
market_end = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
})
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # For memory issues

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(url)
    logger.info("✓ Browser loaded")
    
    iteration = 0
    while True:
        iteration += 1
        current_time = datetime.now()
        
        # Check market hours (9:15 AM to 3:30 PM)
        if not (market_start <= current_time <= market_end):
            logger.info(f"Market closed ({current_time.strftime('%H:%M:%S')}). Waiting for next session...")
            # Wait 1 hour before checking again
            time.sleep(3600)
            continue
        
        logger.info(f"\n--- Iteration {iteration} ({current_time.strftime('%H:%M:%S')}) ---")
        
        retry_count = 0
        success = False
        
        while retry_count < MAX_RETRIES and not success:
            try:
                # Wait for CSV button
                csv_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="CSV"]'))
                )
                csv_link.click()
                logger.info("✓ CSV clicked")
                
                # Wait for download
                initial_files = set(os.listdir(download_path))
                timeout = time.time() + 10
                
                while time.time() < timeout:
                    current_files = set(os.listdir(download_path))
                    new_files = current_files - initial_files
                    if new_files and not any(f.endswith('.crdownload') for f in new_files):
                        break
                    time.sleep(0.3)
                
                # Get latest file
                files = sorted(
                    [f for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f))],
                    key=lambda x: os.path.getmtime(os.path.join(download_path, x)),
                    reverse=True
                )
                
                if files:
                    latest_file = files[0]
                    filepath = os.path.join(download_path, latest_file)
                    
                    # Read CSV
                    df = pd.read_csv(filepath)
                    data = df.to_dict('records')
                    logger.info(f"✓ Read {len(df)} rows from CSV")
                    
                    # Send to API
                    try:
                        response = requests.post(
                            f"{API_URL}/api/data/insert",
                            json=data,
                            timeout=15
                        )
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"✓ API Success: {result}")
                            success = True
                        else:
                            logger.error(f"✗ API Error (Status {response.status_code}): {response.text}")
                            retry_count += 1
                    except Exception as e:
                        logger.error(f"✗ API Connection Error: {e}")
                        retry_count += 1
                    
                    if success:
                        # Rename file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        _, ext = os.path.splitext(latest_file)
                        new_name = f"15_minutes_{timestamp}{ext}"
                        os.rename(filepath, os.path.join(download_path, new_name))
                        logger.info(f"✓ Renamed to: {new_name}")
                else:
                    logger.warning("✗ No files found in download folder")
                    retry_count += 1
                
            except Exception as e:
                logger.error(f"✗ Error: {e}")
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds ({retry_count}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)
        
        if not success:
            logger.warning("Failed after all retries. Refreshing page...")
            driver.refresh()
            time.sleep(5)
        
        # Refresh page for next cycle
        driver.refresh()
        
        # Wait 60 seconds until next pull
        logger.info("⏳ Waiting 60 seconds until next pull...")
        time.sleep(60)

except KeyboardInterrupt:
    logger.info("\n⛔ Stopped by user (Ctrl+C)")

except Exception as e:
    logger.critical(f"❌ Critical error: {e}")
    
finally:
    driver.quit()
    logger.info("✓ Browser closed")
    logger.info("Script ended")
