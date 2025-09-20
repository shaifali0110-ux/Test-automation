```python
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import base64

# Define the HTML content for the simulated customer purchase data dashboard.
# This approach allows the script to be self-contained and runnable without
# needing a separate HTML file or a web server. The JavaScript within
# simulates the filtering logic based on dropdown selections.
DASHBOARD_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Customer Purchase Data Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        .hidden { display: none; }
        .data-row { 
            padding: 10px; 
            border: 1px solid #ddd; 
            margin-bottom: 5px; 
            border-radius: 4px; 
            background-color: #ffffff; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        h1, h2 { color: #333; }
        label { margin-right: 10px; font-weight: bold; color: #555; }
        select { 
            padding: 8px; 
            border-radius: 4px; 
            border: 1px solid #ccc; 
            margin-right: 20px; 
            background-color: #fcfcfc;
        }
        div.controls { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
        #results-container { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Customer Purchase Data Dashboard</h1>

    <div class="controls">
        <label for="productCategory">Product Category:</label>
        <select id="productCategory">
            <option value="All">All</option>
            <option value="Apparel">Apparel</option>
            <option value="Electronics">Electronics</option>
            <option value="HomeGoods">Home Goods</option>
        </select>

        <label for="salesRegion">Sales Region:</label>
        <select id="salesRegion">
            <option value="All">All</option>
            <option value="Northeast">Northeast</option>
            <option value="Midwest">Midwest</option>
            <option value="South">South</option>
        </select>
    </div>

    <div id="results-container">
        <h2>Filtered Data:</h2>
        <!-- Sample data rows, initially hidden or shown by JavaScript -->
        <div id="data-apparel-northeast" class="data-row">Apparel - Northeast Sales: $5000 (Detailed Report Link)</div>
        <div id="data-electronics-midwest" class="data-row">Electronics - Midwest Sales: $3000</div>
        <div id="data-apparel-south" class="data-row">Apparel - South Sales: $2000</div>
        <div id="data-homegoods-northeast" class="data-row">Home Goods - Northeast Sales: $1500</div>
        <div id="data-default" class="data-row">Default View: Showing summary of all categories and regions.</div>
        <div id="no-data-message" class="data-row">No data found for the selected filters. Please adjust your criteria.</div>
    </div>

    <script>
        const productCategorySelect = document.getElementById('productCategory');
        const salesRegionSelect = document.getElementById('salesRegion');
        
        // Get all potential data rows within the results container
        const allDataRows = document.querySelectorAll('#results-container .data-row');

        /**
         * Applies the selected filters and updates the displayed data rows.
         */
        function applyFilters() {
            const selectedCategory = productCategorySelect.value;
            const selectedRegion = salesRegionSelect.value;

            // Hide all data rows initially to ensure a clean slate before showing relevant ones
            allDataRows.forEach(row => row.classList.add('hidden'));

            let dataDisplayed = false; // Flag to track if any data was shown

            // Logic to display data based on filter selections
            if (selectedCategory === 'Apparel' && selectedRegion === 'Northeast') {
                // If both 'Apparel' and 'Northeast' are selected, show only that specific data row
                document.getElementById('data-apparel-northeast').classList.remove('hidden');
                dataDisplayed = true;
            } else if (selectedCategory === 'All' && selectedRegion === 'All') {
                // If 'All' is selected for both, show the default/summary data row
                document.getElementById('data-default').classList.remove('hidden');
                dataDisplayed = true;
            }
            // For any other filter combination not explicitly handled above,
            // if no data was displayed, show the "no data" message.
            if (!dataDisplayed) {
                document.getElementById('no-data-message').classList.remove('hidden');
            }
        }

        // Add event listeners to trigger filtering whenever a dropdown selection changes
        productCategorySelect.addEventListener('change', applyFilters);
        salesRegionSelect.addEventListener('change', applyFilters);

        // Initial setup: Set dropdowns to 'All' and apply filters on page load
        productCategorySelect.value = 'All';
        salesRegionSelect.value = 'All';
        applyFilters(); // Call applyFilters once to set the initial dashboard state
    </script>
</body>
</html>
"""

@pytest.fixture(scope="module")
def driver(request):
    """
    Pytest fixture to initialize and quit the Selenium WebDriver for Chrome.
    The 'module' scope ensures the browser is opened once for all tests in this file
    and closed gracefully after all tests are completed.
    """
    # Configure Chrome options for headless execution (no GUI) and other optimizations
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")           # Run Chrome without a visible UI
    chrome_options.add_argument("--no-sandbox")         # Bypass OS security model (needed for some environments)
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
    chrome_options.add_argument("--window-size=1920,1080") # Set a consistent window size for testing

    # Initialize Chrome WebDriver using ChromeDriverManager
    # ChromeDriverManager automatically handles downloading and managing the correct ChromeDriver binary.
    driver_service = ChromeService(ChromeDriverManager().install())
    web_driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    # Yield the WebDriver instance to the test function
    yield web_driver

    # Teardown: This code runs after all tests in the module have completed.
    # It ensures the browser is properly closed, releasing resources.
    web_driver.quit()

def test_filter_customer_purchase_data_by_category_and_region(driver):
    """
    TC1: Verify filtering customer purchase data by a combination of product category and sales region.

    Test Case Description:
    Preconditions: User is logged in as a marketing analyst and has navigated to the customer purchase data dashboard.
                   The dashboard contains sample data for 'Apparel' products and 'Northeast' region.
    Steps:
    1. Navigate to the customer purchase data dashboard.
    2. Locate and select 'Apparel' from the 'Product Category' filter dropdown.
    3. Locate and select 'Northeast' from the 'Sales Region' filter dropdown.
    Expected Result: The dashboard refreshes to display only purchase data pertaining to
                     'Apparel' products sold exclusively in the 'Northeast' region.
                     All other data should be filtered out, and the displayed data should be accurate.
    """
    # Encode the HTML content to Base64 to create a data URL.
    # This allows loading the entire dashboard HTML directly into the browser without a file.
    encoded_html = base64.b64encode(DASHBOARD_HTML_CONTENT.encode('utf-8')).decode('utf-8')
    data_url = f"data:text/html;base64,{encoded_html}"

    # Step 1: Navigate to the customer purchase data dashboard.
    driver.get(data_url)
    
    # Wait for the Product Category dropdown to be present on the page.
    # This ensures the page has fully loaded and its JavaScript has initialized.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "productCategory"))
    )
    
    # Pre-condition check: Verify the initial state of the dashboard.
    # We expect the 'Default View' data to be visible and the specific
    # 'Apparel - Northeast' data to be hidden before applying filters.
    default_data_element = driver.find_element(By.ID, "data-default")
    apparel_northeast_data_element = driver.find_element(By.ID, "data-apparel-northeast")
    
    assert default_data_element.is_displayed(), \
        "Precondition Failed: 'Default View' data should be visible initially."
    assert not apparel_northeast_data_element.is_displayed(), \
        "Precondition Failed: 'Apparel - Northeast' data should be hidden initially."

    # Step 2: Locate and select 'Apparel' from the 'Product Category' filter dropdown.
    product_category_dropdown = Select(driver.find_element(By.ID, "productCategory"))
    product_category_dropdown.select_by_visible_text("Apparel")
    
    # Step 3: Locate and select 'Northeast' from the 'Sales Region' filter dropdown.
    sales_region_dropdown = Select(driver.find_element(By.ID, "salesRegion"))
    sales_region_dropdown.select_by_visible_text("Northeast")

    # Verification: Wait for the expected 'Apparel - Northeast' data to become visible.
    # This is crucial for dynamic pages where content updates after user interaction.
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "data-apparel-northeast"))
    )

    # Verify that the 'Apparel - Northeast' data is displayed and its content is correct.
    apparel_northeast_data = driver.find_element(By.ID, "data-apparel-northeast")
    assert apparel_northeast_data.is_displayed(), \
        "Expected Result Failed: 'Apparel - Northeast' data should be displayed after filtering."
    assert "Apparel - Northeast Sales: $5000" in apparel_northeast_data.text, \
        "Expected Result Failed: Content of 'Apparel - Northeast' data is incorrect."

    # Verify that all other data elements are NOT displayed, confirming successful filtering.
    # This ensures that only the relevant data is shown.
    other_data_elements_ids = [
        "data-electronics-midwest",
        "data-apparel-south",
        "data-homegoods-northeast",
        "data-default",        # Should be hidden as specific filters are applied
        "no-data-message"      # Should be hidden as data *is* found for the selection
    ]

    for data_id in other_data_elements_ids:
        element = driver.find_element(By.ID, data_id)
        assert not element.is_displayed(), \
            f"Expected Result Failed: Data element '{data_id}' should be hidden, but it is displayed."

    print("\nTest Case TC1: Filtering customer purchase data by category and region PASSED successfully.")

```