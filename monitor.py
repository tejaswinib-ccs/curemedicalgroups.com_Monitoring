import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# ============================================================
# CONFIGURATION
# ============================================================

URLS = [
    "https://curemedicalgroups.com/"
]

BASE_FOLDER = "screenshots"
LOG_FILE = "monitoring_log.csv"

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

FROM_EMAIL = "tejaswini.boyenapally@codectrlsolutions.com"
TO_EMAIL = "tejaswini.boyenapally@codectrlsolutions.com"

IST = ZoneInfo("Asia/Kolkata")

# Retry configuration
MAX_RETRIES = 3
RETRY_WAIT = 10
PAGE_WAIT = 15


# ============================================================
# EMAIL ALERT
# ============================================================

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

        print(
            f"Email alert sent successfully. "
            f"Status Code: {response.status_code}"
        )

    except Exception as e:

        print(f"Email failed: {e}")


# ============================================================
# LOG STATUS
# ============================================================

def log_status(url, status):

    timestamp = datetime.now(IST).strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

    with open(LOG_FILE, "a", newline="") as f:

        f.write(
            f'"{timestamp}","{url}","{status}"\n'
        )


# ============================================================
# EMAIL BODY
# ============================================================

def create_email_body(
    url,
    status,
    error_message="",
    attempts=0
):

    checked_time = datetime.now(IST).strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

    return f"""
    <h2>🚨 Website Monitoring Alert</h2>

    <p>Hello Team,</p>

    <p>
        The website monitoring automation detected an issue.
    </p>

    <p>
        <b>Website:</b> {url}
    </p>

    <p>
        <b>Status:</b> {status}
    </p>

    <p>
        <b>Checked Time:</b> {checked_time}
    </p>

    <p>
        <b>Attempts:</b> {attempts}
    </p>

    <p>
        <b>Error:</b> {error_message}
    </p>

    <p>
        Please check the website immediately.
    </p>

    <p>
        Regards,<br>
        Website Monitoring Automation
    </p>
    """


# ============================================================
# SCREENSHOT FOLDER
# ============================================================

now = datetime.now(IST)

year = now.strftime("%Y")
month = now.strftime("%m")

folder_path = os.path.join(
    BASE_FOLDER,
    year,
    month
)

os.makedirs(
    folder_path,
    exist_ok=True
)


# ============================================================
# CHROME CONFIGURATION
# ============================================================

chrome_options = Options()

chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


# ============================================================
# CREATE NEW CHROME DRIVER
# ============================================================

def create_driver():

    return webdriver.Chrome(
        options=chrome_options
    )


# ============================================================
# WEBSITE MONITORING
# ============================================================

for url in URLS:

    status = "DOWN"
    last_error = ""

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        driver = None

        try:

            print(
                f"\n========================================"
            )

            print(
                f"Attempt {attempt}/{MAX_RETRIES}"
            )

            print(
                f"Checking: {url}"
            )

            print(
                f"========================================"
            )


            # ------------------------------------------------
            # CREATE A COMPLETELY NEW CHROME SESSION
            # ------------------------------------------------

            driver = create_driver()

            print(
                "New Chrome session created."
            )


            # ------------------------------------------------
            # OPEN WEBSITE
            # ------------------------------------------------

            driver.get(url)

            print(
                f"Waiting {PAGE_WAIT} seconds "
                f"for page to load..."
            )

            time.sleep(PAGE_WAIT)


            # ------------------------------------------------
            # GET PAGE INFORMATION
            # ------------------------------------------------

            page_title = driver.title

            page_source = driver.page_source.lower()


            print(
                f"Page title: {page_title}"
            )


            # ------------------------------------------------
            # DETECT CLOUDFLARE / VERIFICATION PAGE
            # ------------------------------------------------

            cloudflare_detected = (

                "please wait while your request is being verified"
                in page_source

                or

                "performing security verification"
                in page_source

                or

                "checking your browser"
                in page_source

                or

                "just a moment"
                in page_source

                or

                "verify you are human"
                in page_source

            )


            # ------------------------------------------------
            # DETECT WEBSITE ERROR
            # ------------------------------------------------

            website_error = (

                page_title == ""

                or

                "error" in page_title.lower()

            )


            # =================================================
            # CLOUDFLARE DETECTED
            # =================================================

            if cloudflare_detected:

                last_error = (
                    "Cloudflare verification page detected"
                )

                print(
                    "⚠ Cloudflare verification page detected."
                )


                if attempt < MAX_RETRIES:

                    print(
                        "Closing current Chrome session..."
                    )

                    driver.quit()

                    driver = None


                    print(
                        f"Waiting {RETRY_WAIT} seconds "
                        f"before retry..."
                    )

                    time.sleep(RETRY_WAIT)

                    continue


                else:

                    status = "DOWN"

                    print(
                        "Maximum retries reached."
                    )

                    print(
                        "Website could not be verified."
                    )


            # =================================================
            # NORMAL WEBSITE ERROR
            # =================================================

            elif website_error:

                last_error = (
                    "Page title is empty or contains error"
                )

                print(
                    "⚠ Website error detected."
                )


                if attempt < MAX_RETRIES:

                    print(
                        "Closing current Chrome session..."
                    )

                    driver.quit()

                    driver = None


                    print(
                        f"Waiting {RETRY_WAIT} seconds "
                        f"before retry..."
                    )

                    time.sleep(RETRY_WAIT)

                    continue


                else:

                    status = "DOWN"

                    print(
                        "Maximum retries reached."
                    )


            # =================================================
            # WEBSITE IS UP
            # =================================================

            else:

                status = "UP"

                timestamp = datetime.now(
                    IST
                ).strftime(
                    "%Y%m%d_%H%M%S"
                )


                filename = (
                    f"{url.replace('https://', '').replace('/', '_')}"
                    f"_{timestamp}.png"
                )


                full_path = os.path.join(
                    folder_path,
                    filename
                )


                # Save screenshot ONLY after successful load
                driver.save_screenshot(
                    full_path
                )


                print(
                    "✓ Website loaded successfully."
                )

                print(
                    f"✓ Screenshot saved: {full_path}"
                )


                # Stop retrying because website is UP
                break


        # =====================================================
        # EXCEPTION
        # =====================================================

        except Exception as e:

            last_error = str(e)

            print(
                f"⚠ Error during attempt {attempt}: {e}"
            )


            if attempt < MAX_RETRIES:

                if driver:

                    print(
                        "Closing current Chrome session..."
                    )

                    driver.quit()

                    driver = None


                print(
                    f"Waiting {RETRY_WAIT} seconds "
                    f"before retry..."
                )

                time.sleep(RETRY_WAIT)

                continue


            else:

                status = "DOWN"

                print(
                    "Maximum retries reached."
                )


        # =====================================================
        # ALWAYS CLOSE BROWSER
        # =====================================================

        finally:

            if driver:

                driver.quit()


    # =========================================================
    # FINAL RESULT
    # =========================================================

    print(
        f"\n========================================"
    )

    print(
        f"FINAL RESULT: {url} - {status}"
    )

    print(
        f"========================================"
    )


    # =========================================================
    # SAVE ONLY FINAL STATUS TO LOG
    # =========================================================

    log_status(
        url,
        status
    )


    # =========================================================
    # SEND EMAIL ONLY IF ALL RETRIES FAIL
    # =========================================================

    if status == "DOWN":

        send_email_alert(

            subject=f"🚨 Website DOWN Alert - {url}",

            body=create_email_body(
                url,
                status,
                last_error,
                MAX_RETRIES
            )
        )