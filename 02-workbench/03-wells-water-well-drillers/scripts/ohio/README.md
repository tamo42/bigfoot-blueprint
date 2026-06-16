# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_enrich_ohio_wells.py`
*   **What it does:** Enriches the Ohio state-specific database with geographic place information. It leverages a general place enrichment module and, by default, operates in a cache-only mode to avoid making new external API queries.
*   **Why it does it:** To update or augment the Ohio database with standardized and enriched place data, utilizing existing cached results to manage costs and provide a foundational layer of geographic information. It acts as a state-specific wrapper for a general place enrichment process.
*   **Inputs:**
    *   An existing database file for the state of Ohio, whose path is determined by `utils.get_db_path("ohio")`.
    *   Cached place data, managed by the `p3_enrich_places` module (potentially stored within the database or an external cache).
*   **Outputs:**
    *   An updated Ohio state database file (e.g., `ohio.db`) with enriched place information.
    *   Informational messages printed to standard output.

### `p2_inspect_ohio_pdf.py`
* **What it does:** Reads a specific PDF document for Ohio's registered PWS contractors, extracts the text layout from its first five pages (or fewer if the document is shorter), and saves this diagnostic text to a plain text file.
* **Why it does it:** To allow for manual inspection of the PDF's text content and layout, aiding in understanding its structure and preparing for more robust data extraction or parsing. It serves as a diagnostic step to confirm text readability and formatting.
* **Inputs:**
    *   `cache\ohio_registered_pws_contractors.pdf`: The source PDF file containing information on Ohio's registered PWS contractors.
    *   `../general/p3_utils.py`: A local utility module used for resolving file paths.
* **Outputs:**
    *   `02-workbench\03-wells-water-well-drillers\ohio_pdf_text_sample.txt`: A plain text file containing the extracted text layout from the initial pages of the input PDF, separated by page breaks, for diagnostic purposes.

### `p2_parse_ohio_pdf.py`
*   **What it does:** This script parses a PDF file containing a list of registered Public Water System Contractors in Ohio. It extracts detailed information for each contractor, including company name, address, contact details, services offered, and licensing information. The extracted data is then cleaned and stored in a SQLite database.
*   **Why it does it:** It automates the extraction of structured contractor data from an unstructured PDF document, making the information queryable and usable for further processing or display, as part of a larger data collection and management pipeline.
*   **Inputs:**
    *   `cache\ohio_registered_pws_contractors.pdf`: The PDF document containing the Ohio PWS contractor listings.
    *   `../general/p3_utils.py`: A helper module for path resolution, phone number cleaning, and slug generation.
    *   `../general/p3_schema.py`: A helper module for initializing the SQLite database schema.
*   **Outputs:**
    *   `data\ohio_pws_contractors.db`: A SQLite database file containing a table (`installers_haulers`) populated with the parsed contractor data from the PDF.
    *   (Optional) A temporary file named `ohio_registered_pws_contractors.pdf.clean` is created if the input PDF has header byte pollution, which is then removed after processing.
    *   Standard output (console) messages indicating the parsing progress, file checks, and the number of records inserted into the database.

### `p2_scrape_ohio.py`
*   **What it does:** This script uses Playwright to navigate to a specific Ohio Department of Health webpage, locate the first PDF download link on that page, and then downloads the PDF file. The downloaded PDF is saved to a `cache` directory within the workspace.
*   **Why it does it:** The script automates the process of obtaining the latest list of registered private water systems contractors from the Ohio Department of Health website. This is useful for regularly acquiring and archiving this specific public data without manual intervention.
*   **Inputs:**
    *   The hardcoded URL: `https://odh.ohio.gov/know-our-programs/private-water-systems-program/media/list-regpwsc-ohio`
    *   The `p3_utils` module, expected to be located in `../general/p3_utils.py`, which provides path resolution utilities.
*   **Outputs:**
    *   A PDF file named `ohio_registered_pws_contractors.pdf` saved to a `cache` directory (e.g., `workspace_root/cache/ohio_registered_pws_contractors.pdf`).
    *   Informative messages and status updates printed to the console regarding browser launch, navigation, link discovery, download status, and file saving.