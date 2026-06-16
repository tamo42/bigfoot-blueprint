# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_investigate_pa.py`
*   **What it does:** Scrapes and parses the Pennsylvania Department of Conservation and Natural Resources (DCNR) website to extract information about licensed drillers. It navigates a main HTML table to get primary company details and then parses nested child tables for additional license-specific details.
*   **Why it does it:** To programmatically extract and structure data about licensed drillers from the specified Pennsylvania DCNR web page, likely for analysis, record-keeping, or further processing.
*   **Inputs:**
    *   **Hardcoded URL:** `https://www.iframeapps.dcnr.pa.gov/topogeo/LicensedDriller` (the web page containing the driller information).
    *   **HTML content:** The web page's HTML structure retrieved from the specified URL.
*   **Outputs:**
    *   **Console Output:**
        *   The total count of valid driller records found.
        *   The full dictionary representation of the first three parsed driller records.
        *   The full dictionary representation of the last two parsed driller records.
        *   Error messages if the web request or parsing fails.

### `p2_scrape_pennsylvania.py`
*   **What it does:** This script scrapes the Pennsylvania Department of Conservation and Natural Resources (DCNR) website for a list of licensed well drillers. It extracts details such as company name, contact information, full address (street, city, state, zip), license number, services offered, and counties served. The parsed data is then stored or updated in a local SQLite database.
*   **Why it does it:** The script automates the collection and structuring of publicly available well driller information from the Pennsylvania DCNR, making it accessible in a local database for further processing, analysis, or integration into an application or directory.
*   **Inputs:**
    *   **External Website**: The Pennsylvania DCNR Licensed Driller roster page (`https://www.iframeapps.dcnr.pa.gov/topogeo/LicensedDriller`).
    *   **Helper Modules**: `general.p3_utils` (for path resolution, slugification, phone number cleaning, and database path retrieval) and `general.p3_schema` (for initializing the SQLite database schema).
*   **Outputs:**
    *   **SQLite Database**: A database file (e.g., `installers_haulers.db`) located in a `data/pennsylvania` directory relative to the project root. This database will contain a table named `installers_haulers`, populated with the scraped driller information, including fields like `name`, `slug`, `address`, `city`, `state`, `zip_code`, `county`, `phone_number`, `served_counties`, `listing_content`, and `pumper_certification_level`.
    *   **Console Output**: Informative messages regarding the scraping process, HTML parsing, the number of records found, and a summary of database insertions and updates. Error messages are printed if issues occur during fetching or database operations.