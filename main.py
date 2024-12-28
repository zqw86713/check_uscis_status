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


def send_email(subject, body, recipient_emails):
    """
    Sends an email with the specified subject and body to multiple recipients.

    :param subject: Email subject
    :param body: Email body
    :param recipient_emails: List of recipient email addresses
    """

    # Retrieve credentials from environment variables
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(
            recipient_emails
        )  # Join recipient emails with commas
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


# Function to save status to a local file
def save_status(status, file_path="uscis_case_status.txt"):
    """
    Saves the given status to a specified file.

    :param status: The USCIS case status to save.
    :param file_path: The path to the file where the status will be saved.
    """
    try:
        with open(file_path, "w") as file:
            file.write(status)
        print(f"Status successfully saved to {file_path}")
    except IOError as e:
        print(f"Failed to save status: {e}")


def read_previous_status(file_path="uscis_case_status.txt"):
    """
    Reads the previous USCIS case status from a file if it exists.

    :param file_path: The path to the file containing the previous status.
    :return: The status as a string, or None if the file does not exist.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return file.read().strip()
        except IOError as e:
            print(f"Failed to read status file: {e}")
    return None


# Function to detect platform and return the correct path to chromedriver
def get_chromedriver_path():
    system_platform = platform.system().lower()

    if system_platform == "windows":
        chromedriver_path = (
            current_working_directory + "/chromedriver-win64/chromedriver.exe"
        )

    elif system_platform == "linux":
        chromedriver_path = (
            current_working_directory + "/chromedriver-linux64/chromedriver"
        )  # Adjust this path if necessary
    else:
        raise Exception(
            "Unsupported platform. Only Windows and Linux are supported."
        )

    return chromedriver_path


# Function to check USCIS case status
def check_case_status(receipt_num):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "start-maximized"
    )  # Ensure the window is maximized in headless mode
    chrome_options.add_argument(
        "--remote-debugging-port=9222"
    )  # Optional debugging option

    # Get the appropriate chromedriver path based on the operating system
    chromedriver_path = get_chromedriver_path()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # USCIS case status website
    USCIS_WEBSITE = "https://egov.uscis.gov/casestatus/landing.do"

    try:
        driver.get(USCIS_WEBSITE)

        # Wait for the input field to be available
        receipt_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "receipt_number"))
        )
        receipt_input.clear()
        receipt_input.send_keys(receipt_num)

        # Click the "Check Status" button
        check_status_button = driver.find_element(By.NAME, "initCaseSearch")
        check_status_button.click()

        # Wait for 10 seconds after input
        time.sleep(10)

        # Now, wait for the status message to load
        status_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "conditionalLanding")
            )
        )

        # Extract and return the status text
        case_status = status_element.text.strip()

        # Split by newline and get the first part
        status_headline = case_status.split("\n")[0]

        # Get the current date and time for the subject line, in Toronto timezone
        tz = pytz.timezone("America/Toronto")
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        # Read the previous status from the file if it exists
        file_path = os.path.join(
            current_working_directory, "uscis_case_status.txt"
        )
        previous_status = read_previous_status(file_path)

        if previous_status is None:
            # First time check, save the status
            subject = f"USCIS Case Status Initial Check - {current_time}"
            body = f"Your USCIS case status: {case_status}"
        elif previous_status != case_status:
            # Status has changed, save the new status
            subject = f"USCIS Case Status Changed - {status_headline} - {current_time}"
            body = f"Your USCIS case status has changed. New Status: {case_status}"
        else:
            # Status did not change
            subject = f"USCIS No Change - {status_headline} - {current_time}"
            body = f"The USCIS case status has not changed."

        # Save the status to a file.
        save_status(
            case_status,
            os.path.join(current_working_directory, "uscis_case_status.txt"),
        )

        # Send email to multiple recipients
        recipient_emails = [
            "qzhang.canada@gmail.com",
            # "recipient2@example.com", # Add more emails as needed
        ]

        # Send the email
        send_email(
            subject=subject, body=body, recipient_emails=recipient_emails
        )

        return case_status

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    # get the current directory which this file is in
    current_working_directory = os.path.dirname(os.path.realpath(__file__))

    my_receipt_number = os.getenv("RECEIPT_NUMBER")
    status = check_case_status(my_receipt_number)
    if status:
        print("Case Status:")
        print(status)
    else:
        print("Failed to retrieve the case status. Please try again.")
