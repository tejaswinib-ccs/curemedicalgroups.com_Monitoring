import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ====== CONFIGURATION ======
URLS = [
    "https://curemedicalgroups.com/",   # replace with your actual URLs
]

SAVE_FOLDER = "screenshots"
LOG_FILE = "monitoring_log.csv"

# ===========================

# Create folder if not exists
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

def log_status(url, status):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()},{url},{status}\n")

for url in URLS:
    try:
        driver.get(url)
        time.sleep(5)

        if driver.title == "" or "error" in driver.title.lower():
            status = "DOWN"
        else:
            status = "UP"

            # Take screenshot
            filename = f"{SAVE_FOLDER}/{url.replace('https://','').replace('/','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(filename)

            print(f"{url} - {status}")
            log_status(url, status)

    except Exception as e:
        print(f"{url} - ERROR: {e}")
        log_status(url, "ERROR")

driver.quit()