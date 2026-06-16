# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_inspect_virginia.py`
*   **What it does:** Streams and displays the first 100 lines of a text file from a hardcoded Virginia Department of Professional and Occupational Regulation (DPOR) URL, attempting to decode lines with UTF-8 and falling back to Windows-1252.
*   **Why it does it:** To perform a quick inspection or reconnaissance of the content of a public-facing regulatory list or dataset provided by the Virginia DPOR without downloading the entire file. This helps in understanding the data format and encoding.
*   **Inputs:**
    *   A hardcoded URL (`https://www.dpor.virginia.gov/sites/default/files/Records%20and%20Documents/Regulant%20List/2705b__crnt.txt`) pointing to a remote text file.
    *   Requires active network connectivity to access the specified URL.
*   **Outputs:**
    *   Prints the first 100 decoded lines of the remote text file to the standard output (console), each prefixed with its 2-digit line number.
    *   Prints error messages to the standard output if an exception occurs during the fetching or processing of the data (e.g., network errors, server issues).

### `p2_scrape_virginia.py`
*   **What it does:** This script scrapes contractor license data from the Virginia Department of Professional and Occupational Regulation (DPOR) website. It downloads several tab-separated text files containing lists of licensed contractors, parses them, filters for records identified as well drillers (either directly certified or general contractors with "WW" specialties), and then extracts and organizes relevant information such as name, address, license details, and contact information. Finally, it stores this structured data into an `installers_haulers` table within a SQLite database.
*   **Why it does it:** It collects and standardizes public data on well drilling contractors in Virginia, providing a structured dataset for further use, such as populating a directory or search application. It aims to ensure data quality by deduplicating records and formatting information consistently.
*   **Inputs:**
    *   **External Data:** Tab-separated text files listing licensed contractors, downloaded from `https://www.dpor.virginia.gov/sites/default/files/Records%20and%20Documents/Regulant%20List/`.
    *   **Configuration:** The `DPOR_FILES` dictionary within the script, which defines the filenames and metadata for the files to be scraped.
    *   **Existing Database:** An optional existing SQLite database (e.g., `virginia.db` in a `data` directory) if previously created by `p3_schema.py`.
    *   **Cached Files:** Previously downloaded contractor files stored in the `cache` directory, which the script will reuse to avoid re-downloading.
*   **Outputs:**
    *   **Cached Files:** Downloaded tab-separated text files (e.g., `virginia_2705a__crnt.txt`) stored in a `cache` subdirectory within the project's workspace.
    *   **SQLite Database:** An updated SQLite database (e.g., `data/virginia.db`) containing a populated `installers_haulers` table with well drilling contractor information from Virginia.
    *   **Console Output:** Progress messages indicating file downloads, processing status, and database ingestion statistics (records inserted/updated).