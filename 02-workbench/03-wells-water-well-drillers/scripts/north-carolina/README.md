# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_explore_nc.py`
* **What it does:** Fetches the HTML content of the "Find Contractor" page from the `ncwelldriller.org` website. It prints the HTTP status code, the final URL, and the first 2000 characters of the retrieved webpage content to the console.
* **Why it does it:** To explore or retrieve initial data from the North Carolina Well Driller website, potentially as a reconnaissance step for web scraping or monitoring. It uses a custom User-Agent and disables SSL verification to facilitate access.
* **Inputs:** No direct external inputs. The target URL `https://www.ncwelldriller.org/web/eh/find-contractor` is hardcoded within the script.
* **Outputs:**
    * Prints "Status Code: <HTTP_STATUS_CODE>" to standard output.
    * Prints "URL: <FINAL_URL>" to standard output.
    * Prints the first 2000 characters of the fetched HTML content to standard output.
    * In case of an error during the request, prints an error message "Error: <EXCEPTION_DETAILS>" to standard output.

### `p2_explore_nc_playwright.py`
* **What it does:** This script uses Playwright to launch a headless Chromium browser, navigate to two specific North Carolina government websites, print their titles, capture full-page screenshots, and output a snippet of their HTML content to the console.
* **Why it does it:** It serves as an exploratory script to programmatically access and gather basic information (title, visual snapshot, initial HTML content) from key web pages related to North Carolina public health and well drilling, demonstrating the capabilities of Playwright for web automation and data collection.
* **Inputs:** None. The URLs are hardcoded within the script.
* **Outputs:**
    * Console output displaying navigation messages, page titles, and the first 1000 characters of the HTML content for each visited page.
    * Two PNG image files: `nc_dhhs_screenshot.png` and `nc_welldriller_screenshot.png`, containing full-page screenshots of the respective websites.

### `p2_scrape_north_carolina.py`
*   **What it does:** Reads and processes a CSV file containing certified driller and contractor information for North Carolina. It aggregates personnel and service details for each unique company, then populates or updates an `installers_haulers` table in a SQLite database with these structured company listings.
*   **Why it does it:** To extract, transform, and load publicly available North Carolina driller certification data into a standardized, queryable SQLite database, making the information readily accessible for further application use.
*   **Inputs:**
    *   `Current_Certified_Drillers_List.csv`: A CSV file located in the same directory as the script, containing rows of certified driller information with columns such as 'Employer', 'First Name', 'Last Name', 'Employer State', 'Employer County', 'Employer Phone', 'Cert', 'Level', and service types.
    *   `scripts/general/p3_schema.py`: Defines the database schema and initialization logic.
    *   `scripts/general/p3_utils.py`: Provides utility functions for database path resolution, phone number cleaning, and slug generation.
    *   An existing SQLite database (e.g., `data/north_carolina.db`) will be read if records are to be updated.
*   **Outputs:**
    *   `data/north_carolina.db`: A SQLite database file, which is created or updated.
    *   The `installers_haulers` table within `north_carolina.db` is populated or updated with records for North Carolina companies, including fields like `name`, `slug`, `county`, `state`, `phone_number`, and a formatted `listing_content` string detailing certified personnel and services.
    *   Console output indicating the number of companies aggregated, and the total number of database insertions and updates performed.