import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ====== CONFIGURATION ======
URLS = [
    "https://curemedicalgroups.com/",
]

BASE_FOLDER = "screenshots"
LOG_FILE = "monitoring_log.csv"

# ===========================

# Get current date parts
now = datetime.utcnow() + timedelta(hours=5, minutes=30)
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")

# Create folder path: screenshots/yy/mm/
folder_path = os.path.join(BASE_FOLDER, year, month)

# Create folder if not exists
os.makedirs(folder_path, exist_ok=True)

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

def log_status(url, status):
    timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="") as f:
        f.write(f"{timestamp},{url},{status}\n")

for url in URLS:
    try:
        driver.get(url)
        time.sleep(5)

        if driver.title == "" or "error" in driver.title.lower():
            status = "DOWN"
        else:
            status = "UP"

            # Create filename with yy_mm_dd format
            timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y%m%d_%H%M%S")
            filename = f"{url.replace('https://','').replace('/','_')}_{timestamp}.png"
            full_path = os.path.join(folder_path, filename)

            driver.save_screenshot(full_path)

        print(f"{url} - {status}")
        log_status(url, status)

    except Exception as e:
        print(f"{url} - ERROR: {e}")
        log_status(url, "ERROR")

driver.quit()