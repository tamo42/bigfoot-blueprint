# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_bootstrap_texas_wells.py`
*   **What it does:** This script fetches a comprehensive list of active Water Well Driller/Pump Installer licenses from the Texas Open Data Portal (a SODA API endpoint). It then cleans, formats, and standardizes this data before inserting it into a local SQLite database.
*   **Why it does it:** The script serves to bootstrap or update a local database with current Texas well driller and pump installer information, making it readily available for other applications that require this data (e.g., mapping, search, or analysis of local service providers). It transforms raw public record data into a structured and easily queryable format.
*   **Inputs:**
    *   **External API:** The Texas Open Data Portal SODA API at `https://data.texas.gov/resource/7358-krk7.json`, queried for "Water Well Driller/Pump Installer" records.
    *   **Shared Utilities:** Relies on `p3_utils.py` for path handling (`get_db_path`), phone number cleaning (`clean_phone_number`), and slugification (`slugify`).
    *   **Database Schema:** Relies on `p3_schema.py` for defining and initializing the SQLite database structure.
*   **Outputs:**
    *   **SQLite Database:** Creates or updates a SQLite database file (e.g., `data/texas.sqlite3`) containing an `installers_haulers` table populated with cleaned and formatted well driller/pump installer records.
    *   **Console Output:** Prints progress messages, status updates on API requests, and a summary of inserted and ignored records.

### `p2_scratch_test_texas_api.py`
*   **What it does:** Fetches a small sample of "Water Well Driller/Pump Installer" records from the Texas Open Data Portal API (data.texas.gov) and saves them to a local JSON file.
*   **Why it does it:** This script serves as a connectivity and data retrieval test, demonstrating how to query the Texas Open Data Portal API for specific license types and store the results locally for further processing or as an example dataset.
*   **Inputs:** None. The script uses a hardcoded API endpoint, specific query parameters (`license_type`, `$limit`), and a predetermined output file path.
*   **Outputs:**
    *   Prints status messages, the HTTP status code, the number of records retrieved, and the JSON content of the records to the console.
    *   A JSON file named `sample_texas_well_records.json` containing the fetched "Water Well Driller/Pump Installer" records, located in `02-workbench/03-wells-water-well-drillers/` relative to the workspace root.
    *   Prints error messages to the console if the API request fails or an exception occurs.