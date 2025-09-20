import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration Constants ---
# Replace these placeholder values with the actual URL and locators
# from your application under test.

# The URL of the customer purchase data dashboard.
DASHBOARD_URL = "https://example.com/dashboard"

# Locators for dashboard elements:
# - Main container displaying customer purchase data.
# - Dropdown for filtering by 'Product Category'.
# - Dropdown for filtering by 'Sales Region'.
LOCATOR_DATA_CONTAINER = (By.ID, "customer-purchase-data-table")
LOCATOR_PRODUCT_CATEGORY_DROPDOWN = (By.ID, "product-category-filter")
LOCATOR_SALES_REGION_DROPDOWN = (By.ID, "sales-region-filter")

# Expected default texts for the filter dropdowns when no filter is applied.
EXPECTED_DEFAULT_PRODUCT_CATEGORY_TEXT = "All Categories"
EXPECTED_DEFAULT_SALES_REGION_TEXT = "All Regions"

# Maximum time in seconds to wait for elements to become visible or present.
WAIT_TIMEOUT_SECONDS = 10

# --- Pytest Fixture for Browser Setup and Teardown ---

@pytest.fixture(scope="module")
def driver():
    """
    Sets up a Chrome browser instance for the entire test module and
    ensures it is gracefully closed after all tests are completed.
    
    The 'module' scope means the browser is opened once before the first
    test in the file and closed once after the last test in the file.
    """
    # Configure Chrome options.
    chrome_options = webdriver.ChromeOptions()
    # Uncomment the line below to run Chrome in headless mode (without UI).
    # chrome_options.add_argument("--headless")
    # Add other common options for headless mode if needed:
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the Chrome WebDriver. Selenium Manager automatically handles
    # downloading and setting up the correct ChromeDriver executable.
    web_driver = webdriver.Chrome(options=chrome_options)
    web_driver.maximize_window() # Maximize the browser window for full view.
    
    # Yield the WebDriver instance to the test functions.
    # Code before yield runs as setup, code after yield runs as teardown.
    yield web_driver
    
    # Teardown: Quit the driver after all tests in the module are finished.
    web_driver.quit()

# --- Test Case Implementation ---

def test_initial_dashboard_state(driver):
    """
    TC1: Verify initial dashboard state displays all data without filters.
    
    Preconditions: User is logged in and on the customer purchase data dashboard.
    Steps:
    1. Navigate to the dashboard URL.
    2. Observe the data displayed on the dashboard.
    3. Observe the state of the 'Product Category' and 'Sales Region' filter dropdowns.
    
    Expected Result:
    - The dashboard displays all available customer purchase data.
    - Both filter dropdowns are in their default/unselected state (e.g., 'All Categories' or 'Select Category').
    """
    
    print(f"\nStarting TC1: Verifying initial dashboard state at {DASHBOARD_URL}")
    
    # Step 1: Navigate to the dashboard URL.
    driver.get(DASHBOARD_URL)
    
    # Initialize WebDriverWait for explicit waits.
    wait = WebDriverWait(driver, WAIT_TIMEOUT_SECONDS)

    # Step 2: Observe the data displayed on the dashboard.
    # Verify that the main data container is visible, indicating that data has loaded.
    # In a real application, you might also check for the number of rows in a table,
    # or the presence of specific data elements. Here, visibility of the container
    # is used as a proxy for "displays all available data".
    try:
        data_container = wait.until(
            EC.visibility_of_element_located(LOCATOR_DATA_CONTAINER),
            message=f"Timed out waiting for data container located by {LOCATOR_DATA_CONTAINER} to be visible."
        )
        assert data_container.is_displayed(), "Dashboard data container is not displayed, indicating data might not be loaded."
        print("Verification: Dashboard data container is displayed.")
        
        # Example of an additional check if the data is in a table:
        # table_rows = driver.find_elements(By.XPATH, f"{LOCATOR_DATA_CONTAINER[1]}//tr")
        # assert len(table_rows) > 1, "Expected more than just header row in data table."
            
    except Exception as e:
        pytest.fail(f"Failed to verify dashboard data display: {e}")

    # Step 3: Observe the state of the 'Product Category' and 'Sales Region' filter dropdowns.
    # Verify both filter dropdowns are in their default/unselected state.
    
    # Verify Product Category Dropdown state.
    try:
        product_category_dropdown = wait.until(
            EC.visibility_of_element_located(LOCATOR_PRODUCT_CATEGORY_DROPDOWN),
            message=f"Timed out waiting for Product Category dropdown located by {LOCATOR_PRODUCT_CATEGORY_DROPDOWN} to be visible."
        )
        # Get the currently displayed text of the dropdown to check its default state.
        # This assumes the default text is directly visible on the dropdown element itself.
        current_product_category_text = product_category_dropdown.text.strip()
        print(f"Verification: Product Category Dropdown text is '{current_product_category_text}'.")
        
        assert current_product_category_text == EXPECTED_DEFAULT_PRODUCT_CATEGORY_TEXT, \
            f"Product Category filter is not in default state. Expected '{EXPECTED_DEFAULT_PRODUCT_CATEGORY_TEXT}', " \
            f"but found '{current_product_category_text}'."
        print(f"Result: Product Category filter is correctly in the default state: '{EXPECTED_DEFAULT_PRODUCT_CATEGORY_TEXT}'.")
            
    except Exception as e:
        pytest.fail(f"Failed to verify Product Category filter dropdown state: {e}")

    # Verify Sales Region Dropdown state.
    try:
        sales_region_dropdown = wait.until(
            EC.visibility_of_element_located(LOCATOR_SALES_REGION_DROPDOWN),
            message=f"Timed out waiting for Sales Region dropdown located by {LOCATOR_SALES_REGION_DROPDOWN} to be visible."
        )
        # Get the currently displayed text of the dropdown to check its default state.
        current_sales_region_text = sales_region_dropdown.text.strip()
        print(f"Verification: Sales Region Dropdown text is '{current_sales_region_text}'.")
        
        assert current_sales_region_text == EXPECTED_DEFAULT_SALES_REGION_TEXT, \
            f"Sales Region filter is not in default state. Expected '{EXPECTED_DEFAULT_SALES_REGION_TEXT}', " \
            f"but found '{current_sales_region_text}'."
        print(f"Result: Sales Region filter is correctly in the default state: '{EXPECTED_DEFAULT_SALES_REGION_TEXT}'.")
            
    except Exception as e:
        pytest.fail(f"Failed to verify Sales Region filter dropdown state: {e}")

    print("TC1: Initial dashboard state successfully verified. Data is displayed and filters are in their default states.")