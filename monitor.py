import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ====== CONFIGURATION ======
URLS = [
    "https://this-domain-does-not-exist-123456789.com"
]

BASE_FOLDER = "screenshots"
LOG_FILE = "monitoring_log.csv"

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

FROM_EMAIL = "tejaswini.boyenapally@codectrlsolutions.com"
TO_EMAIL = "tejaswini.boyenapally@codectrlsolutions.com"

IST = ZoneInfo("Asia/Kolkata")
# ===========================


def send_email_alert(subject, body):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        html_content=body
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email alert sent successfully. Status Code: {response.status_code}")

    except Exception as e:
        print(f"Email failed: {e}")


def log_status(url, status):
    timestamp = datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p")

    with open(LOG_FILE, "a", newline="") as f:
        f.write(f'"{timestamp}","{url}","{status}"\n')


def create_email_body(url, status, error_message=""):
    checked_time = datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p")

    return f"""
    <h2>🚨 Website Monitoring Alert</h2>

    <p>Hello Team,</p>

    <p>The website monitoring automation detected an issue.</p>

    <p><b>Website:</b> {url}</p>
    <p><b>Status:</b> {status}</p>
    <p><b>Checked Time:</b> {checked_time}</p>
    <p><b>Error:</b> {error_message}</p>

    <p>Please check the website immediately.</p>

    <p>Regards,<br>
    Website Monitoring Automation</p>
    """


now = datetime.now(IST)
year = now.strftime("%Y")
month = now.strftime("%m")

folder_path = os.path.join(BASE_FOLDER, year, month)
os.makedirs(folder_path, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

for url in URLS:
    try:
        driver.get(url)
        time.sleep(5)

        if driver.title == "" or "error" in driver.title.lower():
            status = "DOWN"

            send_email_alert(
                subject=f"🚨 Website DOWN Alert - {url}",
                body=create_email_body(url, status, "Page title is empty or contains error")
            )

        else:
            status = "UP"

            timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M%S")

            filename = f"{url.replace('https://', '').replace('/', '_')}_{timestamp}.png"
            full_path = os.path.join(folder_path, filename)

            driver.save_screenshot(full_path)

        print(f"{url} - {status}")
        log_status(url, status)

    except Exception as e:
        status = "DOWN"
        error_message = str(e)

        print(f"{url} - DOWN: {error_message}")
        log_status(url, status)

        send_email_alert(
            subject=f"🚨 Website DOWN Alert - {url}",
            body=create_email_body(url, status, error_message)
        )

driver.quit()