# Michigan Water Well Directory Pipeline

This directory contains the pipeline for extracting, cleaning, and enriching the water well driller registry for **Michigan** (Tier 1 Priority).

## Data Source
*   **Agency:** Michigan Department of Environment, Great Lakes, and Energy (EGLE)
*   **Program:** Water Well Construction Registration
*   **Source URL:** [https://www.michigan.gov/egle/about/organization/drinking-water-and-environmental-health/water-well-construction](https://www.michigan.gov/egle/about/organization/drinking-water-and-environmental-health/water-well-construction)
*   **PowerBI Embed:** The actual registry is rendered client-side using a Microsoft PowerBI dashboard. The embed link varies but follows the `app.powerbigov.us` host.

## Extraction Method
Because PowerBI virtualizes data rendering and uses a complex Dictionary-encoded data shape result (`dsr`) over the network, standard HTTP scraping is not viable. 

The primary extraction script (`scrape_michigan.py`) leverages **Playwright** to:
1. Open a headless Chromium browser and navigate to the PowerBI embed URL.
2. Wait for the initial PowerBI API network calls to resolve and the `visual-container` (grid) to load.
3. Automatically scroll the virtualized grid using `mouse.wheel` and `scroll_into_view_if_needed()`, continuously reading the DOM elements (`div[role="row"]`).
4. Read and extract the `innerText` of every rendered row.
5. Parse the newline-delimited grid cell texts into the canonical directory structure (County, Contractor Name, Business Name, Address, Phone, Contractor Type, License Number).
6. Deduplicate entries by company name and city.
7. Insert records into the canonical `michigan_wells.sqlite` database using the shared `/scripts/general/schema.py` tools.

## Runbook
To execute a fresh scrape and load:
```bash
python scripts/michigan/scrape_michigan.py
```

To run the Google Places API enricher over the Michigan database to geocode records and pull reviews:
```bash
python scripts/general/enrich_places_general.py --state michigan
```
