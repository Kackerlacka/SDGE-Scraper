import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Get the logger for this file
_LOGGER = logging.getLogger(__name__)

def run_scraper(username, password):
    """Function to run the scraper and return processed data."""
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Open Chrome in default size (not maximized)
    options.add_argument("--headless")  # Enable headless mode (no UI)
    # Optionally, set a download directory to auto-download files
    prefs = {"download.default_directory": "/config/www/downloads"}  # Update with a path inside Home Assistant OS
    options.add_experimental_option("prefs", prefs)

    # Set up WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the login page
    login_url = "https://myenergycenter.com/portal/PreLogin/Validate"
    driver.get(login_url)

    # Wait for the login fields to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "usernamex")))

    # Find the username and password fields and enter your credentials
    username_field = driver.find_element(By.ID, "usernamex")
    password_field = driver.find_element(By.ID, "passwordx")

    # Use the dynamic username and password fetched from Home Assistant
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Find the Login button and click it
    login_button = driver.find_element(By.ID, "btnlogin")
    login_button.click()

    # After login, wait for the URL to change (indicating a successful login and redirection)
    try:
        WebDriverWait(driver, 10).until(EC.url_changes(login_url))

        # Redirect to the "Usage" page
        driver.get("https://myenergycenter.com/portal/Usage/Index")

        # Wait for the page to load and make sure no modal is blocking
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#select_value_label_0")))

        # If an overlay or modal is present, close it (e.g., a close button with the class "close")
        try:
            close_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "close"))
            )
            close_button.click()  # Close the modal/overlay
        except:
            _LOGGER.info("No modal overlay found.")

        # Scroll the dropdown into view
        meter_dropdown = driver.find_element(By.CSS_SELECTOR, "#select_value_label_0")
        driver.execute_script("arguments[0].scrollIntoView(true);", meter_dropdown)

        # Wait for the meter dropdown to be clickable and select it
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#select_value_label_0"))).click()

        # Wait for the specific meter option to be clickable and select it
        meter_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#select_option_5"))
        )
        meter_option.click()

        # Now that the meter is selected, proceed to select the "daily" button
        daily_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#dailyView"))
        )
        daily_button.click()

        # Wait for the Excel download button to be clickable and click it
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadusage"))
        )
        download_button.click()

        # Wait for download to finish (or timeout)
        time.sleep(5)

        # Process the downloaded Excel file
        download_dir = "/config/www/downloads"  # Update with the correct path for Home Assistant OS
        files = os.listdir(download_dir)
        excel_files = [f for f in files if f.endswith('.xlsx')]
        latest_file = max(excel_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))

        # Read the Excel file into a dataframe
        df = pd.read_excel(os.path.join(download_dir, latest_file), header=None)

        # Set header row and drop initial rows
        df.columns = df.iloc[11]  # Row 12 (index 11) contains column names
        df = df.drop(index=range(12))
        df = df.dropna(axis=1, how='all')  # Remove empty columns

        # Select only the relevant columns (Date, Consumed)
        data = df.iloc[:, [1, 4]]
        data.columns = ['Date', 'Consumed']
        
        # Log the DataFrame content
        _LOGGER.info(f"Scraped Gas Usage Data: {data.head()}")  # Log first few rows of the data
        
        return data  # Return the cleaned data (Date and Consumed)
    
    except Exception as e:
        _LOGGER.error(f"Error during scraping: {e}")
        return None
    finally:
        driver.quit()  # Make sure to close the browser when done
