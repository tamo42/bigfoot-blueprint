# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `02-septic-georgia-grease-trap/scripts/`.

---

### `apply_actual_licenses.py`
*   **What it does:** Clears existing `mwa_fog_compliance_code` and `bibb_septage_permit_num` for all entries in the `installers_haulers` table of a specific SQLite database, then applies actual FOG compliance codes for a few explicitly identified commercial waste haulers.
*   **Why it does it:** To correct or update the `directory.sqlite` database with verified and actual FOG compliance codes for specific haulers, replacing any placeholder or incorrect data.
*   **Inputs:**
    *   **Database:** `c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite` (an SQLite database containing an `installers_haulers` table).
*   **Outputs:**
    *   **Database:** The `installers_haulers` table within `directory.sqlite` is modified. Specifically:
        *   The `mwa_fog_compliance_code` and `bibb_septage_permit_num` columns are set to `NULL` for all records initially.
        *   The `mwa_fog_compliance_code` is then updated for records with `id` 13, 15, and 16 to specific values ('FOG036', 'FOG114-278', 'FOG500').
    *   **Standard Output (Console):** Progress messages, confirmation of database update, and a verification log displaying the `id`, `name`, `mwa_fog_compliance_code`, and `bibb_septage_permit_num` for all `installers_haulers` after the modifications.

### `apply_rigorous_verification.py`
*   **What it does:** Updates specific records in an SQLite database for septic and grease trap service providers, applying detailed verification statuses, DPH certifications, license types, and disposal site information based on predefined criteria. It then displays the updated records for verification.
*   **Why it does it:** To standardize and rigorously verify the data associated with service provider listings, ensuring accurate representation of their services, certifications, and operational status within the `directory.sqlite` database, likely for a website or application.
*   **Inputs:**
    *   `directory.sqlite`: An SQLite database file, located at `c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`, which is expected to contain an `installers_haulers` table.
    *   Hardcoded `listings_status` dictionary within the script, providing specific verification details (service type, DPH certification level, and license status) for 20 listing IDs.
*   **Outputs:**
    *   Modified `directory.sqlite` database file, with updated `installers_haulers` table records reflecting the new `listing_type`, `admin_category`, `listing_img`, `pumper_certification_level`, `license_status`, `disposal_site_partner`, `eo_insurance_limit` (set to NULL), and `coi_status` for the specified listing IDs.
    *   Standard output (console) displaying a success message and a formatted table of selected fields from the updated `installers_haulers` records for verification.

### `batch_enrich.py`
*   **What it does:** Reads a list of company records from a JSON file, generates dynamic descriptive content (including descriptions, quick facts, and Q&A pairs) based on each company's fleet size, and then updates corresponding entries in an SQLite database. It skips specific hardcoded company slugs.
*   **Why it does it:** Automates the enrichment of company listings in a database, ensuring consistent and detailed content for each entry based on specific attributes like fleet size. This reduces manual data entry, standardizes information, and provides valuable content for website listings or internal directories.
*   **Inputs:**
    *   `pending_enrichment.json`: A JSON file containing a list of dictionaries, where each dictionary represents a company with fields like `slug`, `name`, `city`, and `fleet_size`.
    *   `directory.sqlite`: An SQLite database containing a table named `installers_haulers` with existing company records, which will be updated.
*   **Outputs:**
    *   `directory.sqlite`: The SQLite database, with the `installers_haulers` table modified to include generated content in columns such as `listing_content`, `quickfact_best_for`, `quickfact_primary_items`, `quickfact_fee_structure`, `quickfact_access`, `qa_1_question`, `qa_1_answer`, `qa_2_question`, and `qa_2_answer` for processed companies.
    *   Console output: A confirmation message indicating "Batch enrichment completed. Updated X companies."

### `build_statewide_db.py`
* **What it does:** This script processes raw FOG ID data, aggregates it by company, extracts and standardizes contact and fleet information, generates unique slugs for each company, and then populates or updates a SQLite database table (`installers_haulers`) with this structured information. It also creates an intermediate JSON file with the aggregated company data, intended for further external processing or enrichment.
* **Why it does it:** It transforms fragmented FOG ID records into a cohesive dataset for each service company, creating a structured and searchable directory. This enables the management and display of information for "installers/haulers" on a website or application, facilitating a "statewide" directory listing. The intermediate JSON file supports a workflow where LLMs or other agents can enrich the basic company data with more detailed information.
* **Inputs:**
    * `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\extracted_fog_ids.json`: A JSON file containing a list of dictionaries, where each dictionary represents a record with details like company name, phone tag, FOG ID, city, state, and zip code.
* **Outputs:**
    * `C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`: An SQLite database file. It contains an `installers_haulers` table populated with aggregated company data, including name, unique slug, address approximation, city, state, zip code, phone number, fleet size, and a JSON string of truck details (truck tag, FOG ID).
    * `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\pending_enrichment.json`: A JSON file containing the processed and aggregated company records, formatted as a list of dictionaries, intended for subsequent LLM or external data enrichment.

### `enrich_capabilities.py`
*   **What it does:** Connects to a SQLite database, retrieves published installer/hauler records, and enriches their entries by populating service capability and estimated cost columns based on a hardcoded name-matching heuristic.
*   **Why it does it:** To add detailed service capabilities (e.g., whether they serve specific municipal portals, handle indoor/outdoor traps, offer emergency services, or recycle cooking oil) and an estimated cost tier to the `installers_haulers` table, enhancing the data for these entities. This script serves as a foundational step for or a simulation of a more advanced data enrichment process, possibly involving web scraping or LLMs.
*   **Inputs:**
    *   A SQLite database file: `directory.sqlite`, expected at `C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`.
    *   The `installers_haulers` table within this database, specifically records with `post_status = 'publish'`.
*   **Outputs:**
    *   Modifies the `installers_haulers` table within the input `directory.sqlite` database.
    *   Updates columns `serves_municipal_portals`, `services_indoor_traps`, `services_outdoor_interceptors`, `emergency_24_7`, `cooking_oil_recycling`, and `estimated_cost_tier` for specific hauler entries.
    *   Prints status messages to the console indicating haulers being checked and successfully enriched.

### `extract_all_fog_ids.py`
*   **What it does:** Parses a specific PDF document to extract information about commercial haulers, including their company name, city, state, zip code, phone tag, and a unique FOG ID. It identifies FOG IDs using a regex pattern and deduces associated company details from preceding lines in the PDF text. The script then prints a summary of unique companies and their FOG IDs to the console and saves all extracted records into a JSON file.
*   **Why it does it:** To automate the extraction and structuring of specific data (commercial hauler information and FOG IDs) from a PDF document, making the data easily accessible and usable for further processing, analysis, or integration, without manual data entry.
*   **Inputs:**
    *   A PDF file named `2026-approved-commercial-haulers-data-base.pdf`, expected to be located in a `data` directory relative to the script's execution path (specifically, `../data/2026-approved-commercial-haulers-data-base.pdf`).
    *   The PDF is expected to have a consistent structure where FOG IDs (e.g., FOG123-456) are present, and the related company details (company name, city, state, zip, phone tag) appear in the five lines immediately preceding each FOG ID.
*   **Outputs:**
    *   **Console Output:**
        *   The total number of records successfully extracted.
        *   A sorted list of unique company names found, each followed by all associated FOG IDs.
    *   **File Output:**
        *   `extracted_fog_ids.json`: A JSON file created in the `data` directory (`../data/extracted_fog_ids.json`). This file contains an array of JSON objects, where each object represents an extracted record with keys like `company`, `city`, `state`, `zip`, `phone_tag`, `fog_id`, and `page`.

### `find_broken_links.py`
*   **What it does:** Scans `.astro`, `.md`, and `.js` source files within a specified directory to identify potentially broken or outdated internal links. It compares found links against a hardcoded set of valid routes and checks for references to old dynamic link patterns.
*   **Why it does it:** To ensure link integrity within a web project, primarily an Astro site, by detecting references to non-existent pages or deprecated URL structures (e.g., `/listings/`, `/hauler/`) before deployment. This helps in maintaining a healthy site structure and user experience.
*   **Inputs:**
    *   An SQLite database file (`directory.sqlite`) at `c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite` from which it extracts published `installers_haulers` names (though these are not directly used in the `valid_routes` set for checking in this script's current logic, only for initial data fetching).
    *   Source code files (`.astro`, `.md`, `.js`) located within the `src` directory at `C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src`.
*   **Outputs:**
    *   Informative messages printed to the console indicating each potentially broken or outdated internal link found, including its source file path and the resolved URL.
    *   A final summary count of the total number of potentially broken/outdated internal links discovered during the scan.

### `generate_county_pages.py`
*   **What it does:** Automates the generation of individual Astro component (`.astro`) files for specific Georgia counties. Each generated file serves as a dedicated web page for a grease trap pumping directory, populated with county-specific content, SEO metadata, and dynamic Astro components based on a predefined template.
*   **Why it does it:** To efficiently create and manage a large number of static web pages for different counties, ensuring consistent structure, content, and SEO optimization without manual duplication. This script acts as a static site generator for a localized service directory.
*   **Inputs:**
    *   `counties` dictionary: A Python dictionary containing all county-specific data (e.g., slug, database name, titles, descriptions, FAQs, cities) used to populate the page templates.
    *   `template` string: A multi-line string defining the base structure of an Astro component, including frontmatter, imports, layout, HTML/Astro component markup, and placeholders for dynamic content.
*   **Outputs:**
    *   Multiple `.astro` files, one for each county defined in the `counties` dictionary. These files are saved in the `src/pages/` directory (e.g., `src/pages/macon-bibb.astro`). Each file is a complete Astro component page with county-specific content filled in.

### `get_dph_counties.py`
* **What it does:** This script parses Georgia Department of Public Health (DPH) PDF documents listing certified septic system pumpers and installers. It identifies the county associated with specific company names by detecting county headings within the PDFs.
* **Why it does it:** It aims to automate the process of finding which Georgia county a particular septic or grease trap service company is listed under in official DPH documents, which typically list companies by county. This is useful for data verification or building a database of company service areas.
* **Inputs:**
    * `pdf_path` (string): The file path to a PDF document (e.g., `pumpers.pdf`, `installers.pdf`).
    * `comp_name` (string): The name of the company to search for within the PDF.
    * A hardcoded set of all known Georgia county names used for identification within the PDF text.
    * Specific hardcoded file paths for `pumper_pdf` and `installer_pdf`.
    * A hardcoded list of company names (`comps`) to process.
* **Outputs:**
    * Prints to standard output: For each company found in a PDF, it outputs a formatted string indicating the company name, the detected county, and the page number where it was found.
    * The `get_county_for_match` function returns the county name (string) if the company is found, otherwise `None`.

### `get_license_details.py`
*   **What it does:** Searches through a set of predefined PDF documents for a hardcoded list of company names. When a company name (or a derived search term from it) is found within a PDF, it prints the matching line along with several surrounding lines for context to the console.
*   **Why it does it:** To automate the process of finding and displaying information about specific companies from various licensing or hauler registration PDF documents, making it easier to identify and review relevant entries without manual searching.
*   **Inputs:**
    *   A hardcoded list of 18 company names directly embedded within the `main` function of the script.
    *   Three PDF files: `mwa_haulers.pdf`, `pumpers.pdf`, and `installers.pdf`. These files are expected to be located in a directory named `data`, which itself should be a sibling of the directory containing this script. The script gracefully handles cases where these PDF files do not exist.
*   **Outputs:**
    *   Formatted text output to the console, including:
        *   Headers for each company being searched.
        *   For each PDF file, a message indicating which file is being searched and for which term.
        *   If a match is found: the page number within the PDF, followed by a block of 11 lines of text from the PDF (4 lines before the match, the matching line highlighted with `>>> `, and 6 lines after the match).
        *   Separators (`-` and `=`) for readability between different companies and matches.

### `match_listings.py`
*   **What it does:** This script compares and attempts to match company names from a local SQLite database of installers/haulers with company names found in an external JSON dataset containing FOG (Fats, Oils, and Grease) records. It uses string similarity (SequenceMatcher ratio and substring checks) after standardizing names by cleaning common suffixes and punctuation.
*   **Why it does it:** The script aims to identify potential correspondences between entries in a local directory and records from an external FOG database. This is likely done to enrich the local directory data, cross-reference entries, or identify which local listings correspond to specific FOG permits/records.
*   **Inputs:**
    *   `c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`: A SQLite database containing a table `installers_haulers` with at least `id` and `name` columns.
    *   `c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\extracted_fog_ids.json`: A JSON file structured as a list of dictionaries, where each dictionary represents a FOG record and includes keys like `company`, `fog_id`, `city`, and `phone_tag`.
*   **Outputs:** The script prints results to the standard output (console). For each entry in the SQLite database, it reports:
    *   The DB listing's name and ID.
    *   If a match is found (similarity ratio > 0.5), it displays the best matching FOG company name, the similarity ratio, and details (FOG ID, city, phone) for all associated FOG records.
    *   If no close match is found, it indicates that for the DB listing.

### `parse_rosters.py`
*   **What it does:** Reads a list of installer and hauler names from a local SQLite database and searches for these names within three specified PDF documents (MWA haulers, DPH pumpers, DPH installers). It normalizes names to improve fuzzy matching and prints any found matches to the console.
*   **Why it does it:** To cross-reference and identify which entities listed in a website's directory (from the SQLite database) correspond to entries in official or association rosters provided in PDF format, helping to validate or enrich directory data.
*   **Inputs:**
    *   An SQLite database file located at `C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`. This database is expected to contain an `installers_haulers` table with `id` and `name` columns.
    *   Three PDF files located in a `data` directory adjacent to the script's parent directory: `mwa_haulers.pdf`, `pumpers.pdf`, and `installers.pdf`.
*   **Outputs:**
    *   Information printed to the standard output (console), including:
        *   A script title and separator.
        *   The total page count for each of the three input PDF files.
        *   For each hauler name retrieved from the database:
            *   The name of the hauler being searched.
            *   Any lines (up to 5) found in `mwa_haulers.pdf`, `pumpers.pdf`, or `installers.pdf` that match the hauler's name, along with the page number where they were found.

### `rigorous_cleanup_and_expansion.py`
*   **What it does:** This script connects to a specified SQLite database (`directory.sqlite`), performs schema modifications, purges most existing data, updates metadata for a few specific entries, and then inserts two new, extensively detailed records for commercial grease trap haulers. Specifically, it ensures the `installers_haulers` table has `registered_county` and `served_counties` columns, deletes all records except those with IDs 13, 15, and 16, updates these three retained records with specific county information, and finally adds two new, fully populated entries (Watson Plumbing and Marlers Plumbing Services, LLC) with bios, contact details, service areas, detailed FAQs, and review data.
*   **Why it does it:** The script aims to "rigorously clean up" and "expand" a database of installers/haulers for a website (likely `georgiagreasetrap.com`). The cleanup removes unverified or unwanted listings, focusing the database on a core set of verified providers. The expansion adds highly detailed and optimized content for specific service providers, improving data quality, completeness, and potentially SEO for these key entities by providing comprehensive, structured information. It also ensures the database schema is up-to-date for new county-based filtering.
*   **Inputs:**
    *   A pre-existing SQLite database file located at `c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`.
    *   Hardcoded configuration data within the script for:
        *   IDs of existing records to retain (13, 15, 16).
        *   Specific `registered_county` and `served_counties` data for the retained records.
        *   Comprehensive details (name, bio, phone, address, county, FOG code, extensive FAQs, image URL, current date/timestamp, default values for many other columns) for two new hauler entries (Watson Plumbing and Marlers Plumbing Services, LLC).
*   **Outputs:**
    *   A modified SQLite database file at `c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`. The `installers_haulers` table will contain:
        *   New columns `registered_county` and `served_counties` if they did not exist.
        *   Only five records in total (IDs 13, 15, 16, 21, 22).
        *   Updated county information for records 13, 15, and 16.
        *   Two new, fully populated records for Watson Plumbing (ID 21) and Marlers Plumbing Services, LLC (ID 22), with all specified metadata, FAQs, and default review data.
    *   Console output detailing the script's progress, including column additions, record deletions, updates, and insertions.

### `scrape_ga_sos.py`
* **What it does:** Scrapes the Georgia Secretary of State eCorp Business Search portal to verify the registration status of business entities (installers/haulers) stored in a local SQLite database. For each unverified business, it generates multiple search queries, automates the search on the eCorp website, extracts the business status (e.g., "Active"), and updates the database with the found status and the verification date. If no match is found, it marks the business as "Unverified".
* **Why it does it:** To programmatically verify and update the official business registration status of specific installers and haulers in Georgia, ensuring the accuracy and up-to-dateness of business directory data for a related website, and automating a process that would otherwise be manual and time-consuming.
* **Inputs:**
    *   A local SQLite database file, specifically located at `C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite`. This database contains an `installers_haulers` table with `id`, `name`, `post_status`, and `sos_status` columns, from which unverified businesses (`sos_status IS NULL`) are queried.
    *   The public Georgia Secretary of State eCorp Business Search website (`https://ecorp.sos.ga.gov/BusinessSearch`), which serves as the data source for business verification.
* **Outputs:**
    *   **Updated SQLite database (`directory.sqlite`):** The `installers_haulers` table is modified. For each processed business, the `sos_status` column is updated with the retrieved status (e.g., "Active", "Void", "Inactive", or "Unverified") and the `sos_last_checked` column is updated with the current date.
    *   **Standard Output (Console):** Provides real-time feedback on the script's progress, including the number of haulers being processed, the names of businesses being verified, the search queries attempted, the resulting statuses, and any error messages encountered.