# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_investigate_ny.py`
*   **What it does:** Performs a DuckDuckGo web search for "water well contractor search tool" specifically within the `dec.ny.gov` domain, then extracts and prints only the links from the search results that belong to the `dec.ny.gov` domain.
*   **Why it does it:** To programmatically find relevant pages on the New York State Department of Environmental Conservation (DEC) website pertaining to water well contractor search tools.
*   **Inputs:** None (the search query is hardcoded within the script).
*   **Outputs:** A list of URLs (strings) printed to the standard output (console), filtered to include only those containing "dec.ny.gov". In case of an error during the web request or processing, an error message is printed to the console.

### `p2_investigate_ny_ddg.py`
*   **What it does:** Performs a DuckDuckGo text search for "Water Well Contractor Search Tool" specifically on the `dec.ny.gov` domain, retrieves up to 5 results, and prints them to the console in a JSON format.
*   **Why it does it:** Likely part of an investigation or data gathering process to locate specific resources or tools related to water well contractors on the New York State Department of Environmental Conservation website.
*   **Inputs:** None directly from file or command line; relies on a hardcoded search query and `max_results` parameter. Requires an active internet connection to query DuckDuckGo.
*   **Outputs:** A JSON array printed to standard output (console), containing up to 5 search result objects, each with details such as title, description, and URL.

### `p2_investigate_ny_opendata.py`
*   **What it does:** Fetches a list of datasets (views) from the New York State Open Data API related to the search term "water well", then prints the ID and name of each found dataset to the console.
*   **Why it does it:** To programmatically explore and discover available data related to water wells on the NY Open Data portal, serving as an initial step for potential data integration or analysis projects.
*   **Inputs:** Requires an active internet connection to access `https://data.ny.gov/api/views?q=water%20well`. The search query "water well" is hardcoded within the script.
*   **Outputs:** Prints dataset IDs and names (e.g., `12345 "Water Well Locations"`) to standard output, one per line. In case of an error (e.g., network issue, invalid URL, JSON parsing error), it prints an error message to standard output.

### `p2_investigate_ny_outsystems.py`
*   **What it does:** This script automates interaction with the New York DEC WaterWell Contractor Search OutSystems application using Playwright. It navigates to the search page, switches to "Search By Business Name", types 'a' into the business name field, clicks the search button, and then captures various artifacts. These artifacts include network responses from OutSystems "screenservices" endpoints, a screenshot of the search results, and the full HTML content of the results page.
*   **Why it does it:** It investigates the behavior and data interactions of the specified OutSystems application, likely for reverse engineering, data extraction, or understanding its client-server communication by capturing network payloads and visual state after a search operation.
*   **Inputs:**
    *   **External:** An active internet connection and access to the web application at `https://appfactory.dec.ny.gov/WaterWell/Contractor_Search`.
*   **Outputs:**
    *   `../../scratch/ny_search_page.png`: A full-page screenshot of the search results page after executing the search.
    *   `ny_search_page.html`: A file containing the complete HTML content of the search results page.
    *   `ny_outsystems_responses3.json`: A JSON file containing an array of captured network responses (URL and JSON data) from `screenservices` POST requests made by the OutSystems application during the script's execution.

### `p2_investigate_ny_page.py`
*   **What it does:** This script connects to a specific New York government webpage for water well contractor search, downloads its HTML content, and then parses it to extract and print all hyperlinks found on the page.
*   **Why it does it:** It automates the process of fetching a web page and extracting all embedded `href` attributes (links), likely for initial reconnaissance, link analysis, or as a preliminary step in a larger web scraping or data collection task.
*   **Inputs:** The script uses a hardcoded URL: `https://appfactory.dec.ny.gov/WaterWell/Contractor_Search`.
*   **Outputs:** The script prints the final URL (after any redirects) and a list of all detected hyperlinks (prefixed with "Link:") to the standard output. In case of an error during fetching or parsing, it prints an error message.

### `p2_investigate_post_payload.py`
*   **What it does:** Automates a Chromium browser to visit the NY DEC Water Well Contractor Search page, simulates a search query for drilling companies, and intercepts a specific POST network request to save its payload to a local file.
*   **Why it does it:** To capture and analyze the JSON payload structure used by the `GetWaterwellDrillingCompaniesByName` API endpoint on the NY DEC website, which is useful for reverse-engineering the API's data submission format.
*   **Inputs:** None directly; the script hardcodes the target URL and simulated user interactions.
*   **Outputs:** A file named `ny_post_payload.json` containing the intercepted POST data (payload) from the `GetWaterwellDrillingCompaniesByName` request. Console output provides status updates during execution.

### `p2_scrape_new_york.py`
*   **What it does:** Scrapes water well drilling contractor data from the New York State Department of Environmental Conservation (NY DEC) website. It uses Playwright to navigate the site, intercepts network requests to increase API pagination limits, extracts contractor details from the API responses, and stores them in a local SQLite database.
*   **Why it does it:** To systematically collect and maintain an up-to-date, comprehensive database of water well drilling contractors registered with the NY DEC for New York State, overcoming typical web interface pagination restrictions.
*   **Inputs:**
    *   The NY DEC Water Well Contractor Search web application at `https://appfactory.dec.ny.gov/WaterWell/Contractor_Search`.
    *   Relies on helper functions (`initialize_database`, `get_db_path`, `slugify`, `clean_phone_number`) from `general` utility scripts.
*   **Outputs:**
    *   An SQLite database file (e.g., `new_york.db`) created or updated in the designated data directory.
    *   The `installers_haulers` table within this database, populated with deduplicated contractor information including name, slug, address, city, state, zip code, and phone number. Note: This script clears the `installers_haulers` table at the beginning of each run before inserting new data.
    *   Console output detailing the scraping process, including navigation, records captured, and final insertion statistics.