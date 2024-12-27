from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Define a function to check USCIS case status
def check_case_status(receipt_number):
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Enable for production
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    service = Service('C:\\Users\\HP\\Downloads\\chromedriver-win64\\chromedriver.exe')
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

        # Wait for the status message to load
        status_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "conditionalLanding"))  # Adjust this if needed
        )

        # Extract and return the status text
        case_status = status_element.text.strip()
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
