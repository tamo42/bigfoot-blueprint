# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `background_batch_loop.py`
*   **What it does:** Orchestrates a continuous batch processing loop for data enrichment of `well_contractors` records in an SQLite database. It repeatedly invokes Apify-based enrichment, web crawling, and Gemini AI-based listing enrichment, committing progress to Git after each batch.
*   **Why it does it:** Automates the multi-stage enrichment pipeline for water well contractor data, ensuring records are consistently processed, updated, and persisted to version control until all eligible records are marked as 'enriched' or no further progress can be made.
*   **Inputs:**
    *   An SQLite database (`water_well_directory.sqlite`) containing the `well_contractors` table, where records are identified by their `data_freshness` status.
    *   Three external Python scripts (`p3_enrich_places_apify.py`, `p3_crawl_websites.py`, `p3_enrich_listings.py`) which perform the actual enrichment tasks.
    *   A configured Git environment for version control operations.
*   **Outputs:**
    *   Updated `well_contractors` table in `water_well_directory.sqlite`, specifically the `data_freshness` column, marking records as 'enriched'.
    *   Console log output detailing batch progress, remaining records, and script execution status.
    *   New commits pushed to the remote Git repository, reflecting batch completion.
    *   Potentially, cached crawled website content in a specified local directory by `p3_crawl_websites.py`.

### `clean_messy_names.py`
* **What it does:** Cleans and standardizes contractor names stored in the `well_contractors` table of a specified SQLite database. It removes various noisy patterns such as trailing single letters, content within parentheses, area codes, dates, PO Box information, and address fragments from the `name` column.
* **Why it does it:** To improve the consistency and quality of contractor name data by eliminating irrelevant or inconsistent details, making the data more uniform and suitable for analysis, display, or integration purposes.
* **Inputs:**
    1.  **`water_well_directory.sqlite`**: An SQLite database file expected at `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\data\water_well_directory.sqlite`. The script reads the `id` and `name` columns from the `well_contractors` table within this database.
* **Outputs:**
    1.  **Modified `water_well_directory.sqlite`**: The input SQLite database is updated, specifically the `name` column in the `well_contractors` table, with the cleaned name values.
    2.  **`cleaning_log.txt`**: A new text file created in the script's execution directory. This log file contains a summary of the cleaning operation, including the total number of records updated, and a detailed list showing the original and cleaned names for each modified record.
    3.  **Console Output**: Prints a message indicating the success and the number of records cleaned, directing the user to review `cleaning_log.txt`. Also prints an error message if the database file is not found.

### `p3_enrich_listings.py`
*   **What it does:** Enriches water well contractor listings in a SQLite database by analyzing their crawled website text using the Google Gemini AI model. It extracts specific service details (e.g., emergency services, water testing, permitting), generates a detailed HTML description, and creates a set of canonical Q&As, then updates the database.
*   **Why it does it:** To automate the process of populating a business directory with rich, AI-generated content and structured data, enhancing the utility and completeness of contractor profiles and improving search relevance and user experience.
*   **Inputs:**
    *   `GEMINI_API_KEY` or `GOOGLE_API_KEY` (from environment variables or a `.env` file).
    *   SQLite database containing the `well_contractors` table, including contractor `id`, `name`, `slug`, `website_url`, `city`, `state`, and `county`.
    *   Cached website text files (`02-workbench/03-wells-water-well-drillers/cache/crawled_text/<state_folder_or_general>/<slug>.txt`) for each contractor.
    *   Command-line arguments: `--state` (e.g., `georgia`, `all`), `--mode` (`validation` or `full`), `--limit` (optional integer), and `--db` (optional path to database).
*   **Outputs:**
    *   **SQLite Database:** The `well_contractors` table is updated with numerous new AI-generated fields, including: `emergency_repair_247`, `emergency_response_time`, `emergency_services_offered`, `pressure_tank_services`, `water_testing_offered`, `water_treatment_installed`, `handles_new_permits`, `listing_content` (HTML), `speakable_what_you_find`, `speakable_listing_details`, `speakable_quick_facts`, `quickfact_best_for`, `quickfact_primary_services`, `quickfact_pricing_guide`, `quickfact_service_area`, and `qa_X_question`/`qa_X_answer` pairs. It also sets `enriched_at`, `enrichment_source`, and `data_freshness` to 'enriched'.
    *   **Console Output:** Provides progress updates, status messages, and error notifications during the enrichment process.

### `p3_enrich_places.py`
*   **What it does:** Connects to a specified SQLite database, queries for `well_contractors` records lacking Google Places data for a given state, and enriches these records by making calls to the Google Places API. It retrieves and updates fields such as Google Place ID, website URL, rating, review count, latitude, longitude, and up to three reviews. The script utilizes a local JSON cache to minimize API calls and includes a safety limit for new queries.
*   **Why it does it:** To enhance the `well_contractors` dataset with external, verified business information from Google Places, providing more comprehensive and accurate details (e.g., official contact info, customer feedback, and precise location data) for further analysis and use.
*   **Inputs:**
    *   **Command-line arguments:**
        *   `--state <state_name>`: The state (e.g., `georgia`, `ohio`) to filter contractors for enrichment. Required.
        *   `--db <db_path>`: Optional direct path to the SQLite database. If omitted, the database path is resolved automatically using `p3_utils`.
        *   `--limit <max_queries>`: Optional maximum number of new Google Places API queries to perform during a single run (default: 100).
    *   **Environment variable:** `GOOGLE_PLACES_API_KEY`: An API key for authenticating with the Google Places API, loaded from a `.env` file at the workspace root.
    *   **Files:**
        *   An existing SQLite database (e.g., `unified.db`) containing a `well_contractors` table.
        *   A local JSON cache file (e.g., `data/cache/places/places_cache.json`) storing previously fetched Google Places API responses.
*   **Outputs:**
    *   **Modified SQLite database:** The `well_contractors` table is updated with new columns (`google_place_id`, `website_url`, `google_rating`, `google_review_count`, `manual_lat`, `manual_lng`, `reviews_json`, `review_1_text`, `review_1_author`, `review_1_rating`, `review_2_text`, `review_2_author`, `review_2_rating`, `review_3_text`, `review_3_author`, `review_3_rating`) for enriched records.
    *   **Cache file:** The local JSON cache file (`places_cache.json`) is updated with new Google Places API responses.
    *   **Console output:** Informational messages about progress, cache hits, API calls made, errors encountered, and an estimated cost of the API queries.

### `p3_migrate_databases.py`
*   **What it does:** Consolidates multiple state-specific SQLite databases containing well contractor and pump installer information into a single, unified SQLite database, de-duplicating entries and structuring data according to a predefined schema. It identifies unique companies based on website, phone, or name/city, and then extracts and associates individual technician licenses.
*   **Why it does it:** To create a single, comprehensive, and standardized directory of well contractors and pump installers by merging data from various state sources. This centralization enables easier querying, management, and use of the data for applications or further analysis without dealing with multiple disparate files.
*   **Inputs:**
    *   **File System:** Multiple SQLite database files (e.g., `*.sqlite` excluding `water_well_directory.sqlite`) are expected in the `02-workbench/03-wells-water-well-drillers/data/` directory. These files contain raw contractor/installer data, typically in tables named `well_contractors` or `installers_haulers`.
    *   **External Modules:** Relies on `p3_utils.py` for utility functions (e.g., `resolve_path`, `get_unified_db_path`, `slugify`) and `p3_schema.py` for defining and initializing the target database schema (tables `well_contractors` and `technician_licenses`).
*   **Outputs:**
    *   **File System:**
        *   `02-workbench/03-wells-water-well-drillers/data/water_well_directory.sqlite`: A new or updated SQLite database containing consolidated contractor information in the `well_contractors` and `technician_licenses` tables.
        *   `02-workbench/03-wells-water-well-drillers/data/backup/water_well_directory.sqlite.bak`: A backup of the previous `water_well_directory.sqlite` file, created if one existed before migration.
    *   **Console Output:** Detailed logging of the migration process, including the number of source files processed, total raw records, unique companies identified, and records inserted into the unified database.

### `p3_schema.py`
*   **What it does:** Defines the canonical SQLite database schemas for two tables, `well_contractors` and `technician_licenses`, and provides a function to create or incrementally migrate these tables in a specified SQLite database file.
*   **Why it does it:** This script establishes and maintains the core data model for storing well contractor information and their associated technician licenses, ensuring data consistency and enabling future schema evolution through additive migrations.
*   **Inputs:**
    *   `db_path` (str): The file path to the SQLite database to be initialized or migrated.
*   **Outputs:**
    *   Modifies the SQLite database file at `db_path` by creating the `well_contractors` and `technician_licenses` tables if they don't exist, or by adding any new columns to existing tables.
    *   Prints informational messages to `stdout` regarding table creation and schema migration status.

### `p3_utils.py`
*   **What it does:** Provides a collection of utility functions for path resolution, string manipulation (slugification and phone number cleaning), and loading configuration specific to the project, such as API keys and database paths.
*   **Why it does it:** It centralizes common operations required by other scripts within the `nhq-bigfoot-blueprint` workspace. This promotes consistency in path handling, standardizes string formatting, and simplifies access to frequently used file locations and configuration values, such as the Google Places API key and various SQLite database paths.
*   **Inputs:**
    *   `__file__`: Implicitly used to determine the current script's location for workspace root calculation.
    *   File system: Accesses directories and files (e.g., `.env`, `cache/places_cache.json`, state-specific SQLite databases) to resolve paths and load data.
    *   Strings: Text inputs for slugification, phone numbers for cleaning, relative paths for resolution, and state names for database path generation.
*   **Outputs:**
    *   Absolute file system paths to the workspace root, specific cache files, and SQLite databases.
    *   Cleaned, lowercase, hyphen-separated strings (slugs).
    *   Formatted phone number strings (e.g., `(XXX) XXX-XXXX`).
    *   The `GOOGLE_PLACES_API_KEY` string, if found in the `.env` file.
    *   `None` if the API key is not found or a path does not exist (in the case of `load_env_api_key`).
    *   The original input string if phone number formatting fails.

### `p3_validate_databases.py`
* **What it does:** Validates the schema consistency across multiple SQLite database files stored in a specific data directory. It first ensures each database applies a canonical schema using `p3_schema.initialize_database`, then compares the `well_contractors` table schema (column names and types) of all databases against the first successfully processed database to ensure symmetry.
* **Why it does it:** To maintain data integrity and consistency across state-specific well contractor databases. Inconsistent schemas can lead to errors in data processing, analysis, and integration, so this script verifies that all databases adhere to a uniform structure.
* **Inputs:**
    *   SQLite database files (`.sqlite` extension) located in `02-workbench/03-wells-water-well-drillers/data` relative to the script's execution path. Each file name is expected to represent a state.
    *   The `p3_schema` module, which defines the canonical schema and provides the `initialize_database` function to apply it.
* **Outputs:**
    *   **Console output**: Informative messages detailing the validation process, including which databases are being checked, their column counts, and any detected schema mismatches (missing columns, extra columns, or type mismatches). A final success or failure message is displayed.
    *   **Exit status**: The script exits with status `0` if all database schemas are symmetric and consistent, and `1` if any schema mismatches are found.
    *   **Modified databases (potential)**: The `p3_schema.initialize_database()` function might alter the schema of the input SQLite databases to bring them in line with the canonical definition before validation occurs.

### `test_batch.py`
* **What it does:** Orchestrates a three-step data enrichment pipeline—Apify place enrichment, website crawling, and Gemini listing enrichment—on a limited dataset, then commits and pushes the results to a Git repository.
* **Why it does it:** Automates a sequence of data processing tasks, primarily for testing the end-to-end enrichment workflow on a subset of data (e.g., 100 records), and ensures that the processing results are version-controlled via Git.
* **Inputs:**
    * Hardcoded `WORKSPACE` and `DB_PATH` directory/file paths.
    * Configuration parameters passed as command-line arguments to the subprocesses (e.g., `--state all`, `--limit 100`, `--keywords`, `--workers`).
    * An existing SQLite database (`water_well_directory.sqlite`) containing contractor data.
    * Data from external APIs (Apify, Gemini) and websites accessed during crawling.
    * An initialized Git repository at the `WORKSPACE` path.
* **Outputs:**
    * Standard output messages indicating progress and completion.
    * Modified `water_well_directory.sqlite` database with enriched data.
    * Cached website content files stored in the specified `cache-dir`.
    * Updates to the Git repository (staged, committed, and pushed changes).