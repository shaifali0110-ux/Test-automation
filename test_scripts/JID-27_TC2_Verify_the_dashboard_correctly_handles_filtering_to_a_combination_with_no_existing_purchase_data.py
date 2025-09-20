import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Define the base URL for the dashboard. Replace with your actual dashboard URL.
DASHBOARD_URL = "http://localhost:8000/dashboard" 

@pytest.fixture(scope="module")
def driver():
    """
    Pytest fixture to set up and tear down the Selenium WebDriver for Chrome.
    This ensures a new browser instance for the entire test module.
    """
    # Initialize Chrome WebDriver using webdriver_manager to handle driver binary
    service = ChromeService(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    # Optional: Add any desired Chrome options, e.g., headless mode
    # chrome_options.add_argument("--headless") 
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set an implicit wait to help find elements when they are not immediately available
    driver.implicitly_wait(10)
    
    # Yield the driver instance to the test function
    yield driver
    
    # Teardown: Quit the browser after all tests in the module are done
    driver.quit()

def test_no_data_filter_scenario(driver):
    """
    TC2: Verify the dashboard correctly handles filtering to a combination
    with no existing purchase data.
    """
    # 1. Navigate to the customer purchase data dashboard.
    driver.get(DASHBOARD_URL)

    # Wait for the dashboard to load completely, e.g., by checking for a main element
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dashboardTitle")), 
        "Dashboard title not found, page might not have loaded correctly."
    )

    # Locators for filter elements and the no-data message.
    # These are illustrative. Replace with actual IDs, names, or robust XPath/CSS selectors
    # from your application's HTML.

    # Product Category Filter
    product_category_dropdown_locator = (By.ID, "productCategoryFilterDropdown")
    product_category_option_locator = (By.XPATH, "//ul[@id='productCategoryOptions']/li[text()='Industrial Machinery']")
    
    # Sales Region Filter
    sales_region_dropdown_locator = (By.ID, "salesRegionFilterDropdown")
    sales_region_option_locator = (By.XPATH, "//ul[@id='salesRegionOptions']/li[text()='South Pole']")

    # No Data Message
    no_data_message_locator = (By.ID, "noDataMessage")
    expected_no_data_text = "No data found for the selected filters"

    # 2. Locate and select 'Industrial Machinery' from the 'Product Category' filter dropdown.
    print("Selecting 'Industrial Machinery' from Product Category filter...")
    
    # Click the product category dropdown to open it
    product_category_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(product_category_dropdown_locator),
        f"Product category dropdown not clickable at {product_category_dropdown_locator}"
    )
    product_category_dropdown.click()

    # Click the 'Industrial Machinery' option
    industrial_machinery_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(product_category_option_locator),
        f"'Industrial Machinery' option not clickable at {product_category_option_locator}"
    )
    industrial_machinery_option.click()
    print(" 'Industrial Machinery' selected.")

    # 3. Locate and select 'South Pole' from the 'Sales Region' filter dropdown.
    print("Selecting 'South Pole' from Sales Region filter...")
    
    # Click the sales region dropdown to open it
    sales_region_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(sales_region_dropdown_locator),
        f"Sales region dropdown not clickable at {sales_region_dropdown_locator}"
    )
    sales_region_dropdown.click()

    # Click the 'South Pole' option
    south_pole_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(sales_region_option_locator),
        f"'South Pole' option not clickable at {sales_region_option_locator}"
    )
    south_pole_option.click()
    print(" 'South Pole' selected.")

    # Expected Result: The dashboard refreshes and displays a clear message
    # indicating 'No data found for the selected filters' or a similar informative message.
    print("Waiting for 'No data found' message to appear...")
    no_data_message_element = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(no_data_message_locator),
        f"No data message element not visible at {no_data_message_locator} after filtering."
    )

    # Assert that the message is displayed and contains the expected text.
    actual_message_text = no_data_message_element.text.strip()
    print(f"Actual message received: '{actual_message_text}'")
    
    assert actual_message_text == expected_no_data_text, \
        f"Expected message '{expected_no_data_text}' but got '{actual_message_text}'"
    
    print("Test passed: 'No data found' message displayed correctly.")
    
    # Optional: Verify no data tables are visible if applicable
    # e.g., assert EC.invisibility_of_element_located((By.ID, "customerDataTable")) (replace with actual table ID)