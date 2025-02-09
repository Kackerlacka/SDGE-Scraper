from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

# Assuming username and password are provided by Home Assistant config as input_text entities
username = "home_assistant_username"  # This will come from Home Assistant
password = "home_assistant_password"  # This will come from Home Assistant

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
        print("No modal overlay found.")

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

    # Optionally, you can print the text of the selected meter to confirm
    print(f"Selected Meter: {meter_option.text}")

    # Now that the meter is selected, proceed to select the "daily" button
    daily_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#dailyView"))
    )
    daily_button.click()
    print("Daily usage view selected.")

    # Wait for the Excel download button to be clickable and click it
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadusage"))
    )
    download_button.click()
    print("Download initiated.")

    # Keep the browser open for 5 seconds to visually confirm
    time.sleep(5)

except Exception as e:
    print("Login or redirection did not work as expected.")
    print("Error:", e)
    print("Current URL:", driver.current_url)

# Optionally, continue with scraping or other tasks after this point

# Now that the file is downloaded, locate the most recent downloaded file in the directory
download_dir = "/config/www/downloads"  # Updated to Home Assistant OS path
files = os.listdir(download_dir)

# Filter out the Excel files
excel_files = [f for f in files if f.endswith('.xlsx')]

# Get the most recent Excel file
latest_file = max(excel_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
print(f"Most recent file: {os.path.join(download_dir, latest_file)}")

# Read the Excel file into a pandas dataframe, starting from row 13
df = pd.read_excel(os.path.join(download_dir, latest_file), header=None)  # No header at the beginning

# Set the header row to row 12 (index 11), because row 12 (0-indexed) has the actual column names
df.columns = df.iloc[11]  # Set the 12th row (0-indexed) as the header

# Now drop the first 12 rows, because we have already set the header correctly
df = df.drop(index=range(12))

# Remove any empty columns from the dataframe (which will fix the NaN columns issue)
df = df.dropna(axis=1, how='all')

# Now, let's check the columns and the first few rows to verify everything
print("Columns in the Excel file:", df.columns)
print("First few rows of the dataframe:")
print(df.head())

# Now select only the 'Date' and 'Consumed' columns (which are 2nd and 5th columns, respectively)
data = df.iloc[:, [1, 4]]  # Columns 'Date' (B) and 'Consumed' (E)
data.columns = ['Date', 'Consumed']

# Display the cleaned data
print("Cleaned data (Date vs. Consumed):")
print(data)

# Don't forget to close the driver when done
driver.quit()
