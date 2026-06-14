# New York Water Well Drillers Extraction

## Overview
New York state has ~1.3M private water wells. The New York State Department of Environmental Conservation (NYSDEC) requires all water well contractors to register annually (ECL §15-1525). 

Unlike some states with open data portals or public APIs, the NYSDEC registry is only accessible through the **Water Well Contractor Search Tool**, a custom OutSystems web application located at `https://appfactory.dec.ny.gov/WaterWell/Contractor_Search`.

## Technical Challenges & Approach
1. **OutSystems Web App:** The search tool is a client-side rendered React application built on the OutSystems platform. It fetches data via POST requests to `/WaterWell/screenservices/...` endpoints.
2. **Hidden Pagination:** The web interface natively paginates results to 20 records per request. 
3. **Empty String Validation:** The business name input field uses HTML5 validation to prevent submitting an empty search string.
4. **Data Extraction Solution:** We wrote a Playwright script (`scrape_new_york.py`) that uses **Request Interception** to bypass the API restrictions. The script:
    - Navigates to the search tool using a headless Chromium browser.
    - Intercepts the OutSystems POST request to the `GetWaterwellDrillingCompaniesByName` endpoint.
    - Modifies the JSON payload on-the-fly to change the `"MaxRecords"` and `"MaxRecordsBusinessName"` fields from `20` to `1000`.
    - Automatically inputs a single space `" "` into the Business Name field to pass validation.
    - Captures the entire payload in a single response, effectively downloading all active NY water well drillers (~450+ records).

## Files in this Directory
- `scrape_new_york.py`: The final extraction script that scrapes the data via Playwright request interception, cleans and parses the output, and saves the data to the central SQLite database.
- `investigate_ny_outsystems.py`: Exploration script used to debug the OutSystems framework and capture the raw HTML/screenshots for reverse engineering.
- `investigate_post_payload.py`: Diagnostic script used to capture the exact structure of the POST request JSON payload sent by the OutSystems app.
- `ny_outsystems_responses*.json` & `ny_search_page.*`: Temporary artifacts and raw JSON dumps saved during the investigation phase.

## Runbook
If you need to refresh the New York data in the future:
1. Navigate to this directory in your terminal.
2. Run the extraction script:
   ```powershell
   python scrape_new_york.py
   ```
   *Note: Ensure Playwright is installed (`pip install playwright` and `playwright install chromium`).*
3. The script will automatically intercept the API, fetch all records, clean them, and insert them into the global database (`data/new_york_wells.sqlite`).
4. Run the enrichment script to pull the latest Google Places data:
   ```powershell
   python ../general/enrich_places_general.py --state new_york --limit 500
   ```
