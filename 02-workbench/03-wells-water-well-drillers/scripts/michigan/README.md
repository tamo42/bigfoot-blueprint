# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_scrape_michigan.py`
*   **What it does:** Scrapes water well driller and pump installer data from the Michigan EGLE PowerBI dashboard, extracts relevant contractor information, and stores it in a structured SQLite database.
*   **Why it does it:** To systematically collect and maintain a structured dataset of licensed water well drillers and pump installers in Michigan, as the information is presented dynamically within a PowerBI grid that requires programmatic interaction (scrolling, extracting text) to access all entries.
*   **Inputs:**
    *   A hardcoded URL pointing to the Michigan EGLE PowerBI dashboard.
    *   External helper modules: `p3_utils.py` for utility functions (e.g., database path, phone cleaning, slug generation) and `p3_schema.py` for database schema initialization.
*   **Outputs:**
    *   A SQLite database file (e.g., `data/michigan_installers.db`) containing a table named `installers_haulers` populated with parsed contractor details such as name, address, city, state, zip code, county, phone number, and aggregated license information.
    *   Informational messages printed to the console indicating the scraping progress, number of records found, and database save status.