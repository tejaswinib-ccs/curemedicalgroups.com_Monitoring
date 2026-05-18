import os
import time
import smtplib

from email.message import EmailMessage

from datetime import datetime
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ====== CONFIGURATION ======
URLS = [
    "https://curemedicalgroups.com/"
]

BASE_FOLDER = "screenshots"
LOG_FILE = "monitoring_log.csv"

# Email Configuration
SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")

RECEIVER_EMAIL = "tejaswini.boyenapally@codectrlsolutions.com"

# ===========================

# Indian Standard Time
IST = ZoneInfo("Asia/Kolkata")

# Current IST time
now = datetime.now(IST)

year = now.strftime("%Y")
month = now.strftime("%m")

# Create folder path
folder_path = os.path.join(BASE_FOLDER, year, month)

# Create folder if not exists
os.makedirs(folder_path, exist_ok=True)

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def send_email_alert(subject, body):

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    message.set_content(body)

    try:

        server = smtplib.SMTP("smtp.office365.com", 587)

        server.starttls()

        server.login(
            SENDER_EMAIL,
            SENDER_PASSWORD
        )

        server.send_message(message)

        server.quit()

        print("Email alert sent successfully.")

    except Exception as e:

        print(f"Email failed: {e}")

def log_status(url, status):
    timestamp = datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p")

    with open(LOG_FILE, "a", newline="") as f:
        f.write(f'"{timestamp}","{url}","{status}"\n')

for url in URLS:
    try:
        driver.get(url)
        time.sleep(5)

        if driver.title == "" or "error" in driver.title.lower():

            status = "DOWN"

            send_email_alert(
                "Website DOWN Alert",
                f"The website {url} is DOWN."
            )
        else:
            status = "UP"

            timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M%S")

            filename = (
                f"{url.replace('https://', '').replace('/', '_')}_{timestamp}.png"
            )

            full_path = os.path.join(folder_path, filename)

            driver.save_screenshot(full_path)

        print(f"{url} - {status}")
        log_status(url, status)

    except Exception as e:

        print(f"{url} - ERROR: {e}")

        log_status(url, "ERROR")

        send_email_alert(
        "Website Monitoring ERROR",
        f"Error while checking {url}\n\n{e}"
        )

driver.quit()