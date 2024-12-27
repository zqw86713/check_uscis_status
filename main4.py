import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import pytz
import platform


# Function to send an email notification
def send_email(subject, body, to_email):
    sender_email = "qzhang.usa0116@gmail.com"  # Your email address
    sender_password = "syyz olca bgjd iqnm"  # Your email password (or app password if using Gmail)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use your email provider's SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Function to save status to a local file
def save_status(status):
    with open("uscis_case_status.txt", "w") as file:
        file.write(status)
    print("Status saved to uscis_case_status.txt")


# Function to detect platform and return the correct path to chromedriver
def get_chromedriver_path():
    system_platform = platform.system().lower()

    if system_platform == 'windows':
        chromedriver_path = './chromedriver-win64/chromedriver.exe'
    elif system_platform == 'linux':
        chromedriver_path = './chromedriver-linux64/chromedriver'  # Adjust this path if necessary
    else:
        raise Exception("Unsupported platform. Only Windows and Linux are supported.")

    return chromedriver_path


# Function to check USCIS case status
def check_case_status(receipt_number):
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('start-maximized')  # Ensure the window is maximized in headless mode
    chrome_options.add_argument('--remote-debugging-port=9222')  # Optional debugging option

    # Get the appropriate chromedriver path based on the operating system
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://egov.uscis.gov/casestatus/landing.do")

        # Wait for the input field to be available
        receipt_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "receipt_number"))
        )
        receipt_input.clear()
        receipt_input.send_keys(receipt_number)

        # Click the "Check Status" button
        check_status_button = driver.find_element(By.NAME, "initCaseSearch")
        check_status_button.click()

        # Wait for 10 seconds after input
        time.sleep(10)

        # Now, wait for the status message to load
        status_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "conditionalLanding"))
        )

        # Extract and return the status text
        case_status = status_element.text.strip()

        # Get the current date and time for the subject line, in Toronto timezone
        tz = pytz.timezone('America/Toronto')
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        # Read the previous status from the file if it exists
        previous_status = None
        if os.path.exists("uscis_case_status.txt"):
            with open("uscis_case_status.txt", "r") as file:
                previous_status = file.read().strip()

        # Compare current status with the previous one and send email accordingly
        if previous_status is None:
            # First time check, save the status and send an initial email
            save_status(case_status)
            send_email(
                subject=f"USCIS Case Status Initial Check - {current_time}",
                body=f"Your USCIS case status: {case_status}",
                to_email="qzhang.canada@gmail.com"
            )
        elif previous_status != case_status:
            # Status has changed, save the new status and send an email indicating the change
            save_status(case_status)
            send_email(
                subject=f"USCIS Case Status Changed - {current_time}",
                body=f"Your USCIS case status has changed. New Status: {case_status}",
                to_email="qzhang.canada@gmail.com"
            )
        else:
            # Status did not change, send an email including the previous status
            send_email(
                subject=f"USCIS Case Status Did Not Change - {current_time}",
                body=f"The USCIS case status has not changed. Previous Status: {previous_status}",
                to_email="qzhang.canada@gmail.com"
            )

        return case_status

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    # Qingwei's receipt number.
    receipt_number = "IOE0923949113"
    status = check_case_status(receipt_number)
    if status:
        print("Case Status:")
        print(status)
    else:
        print("Failed to retrieve the case status. Please try again.")
