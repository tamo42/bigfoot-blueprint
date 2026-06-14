# Texas Water Well Contractors Ingestion Runbook

This directory handles harvesting and importing active water well drillers and pump installers for the State of Texas.

---

## Data Source

*   **Agency:** Texas Department of Licensing and Regulation (TDLR)
*   **Source Format:** REST SODA API
*   **Original URL:** [Texas Open Data Portal (TDLR Active Licenses)](https://data.texas.gov/resource/7358-krk7.json)
*   **API Query Filter:** `license_type = 'Water Well Driller/Pump Installer'`

---

## Technical Extraction Process

The Texas dataset is queryable in bulk using Socrata's Open Data API. The bootstrap script works as follows:

1.  **API Call:** Performs a REST request to the Socrata endpoint filtering for the specific license category. The limit is configured to `2500` to retrieve all active records (~1,740 total) in a single request.
2.  **Geocoding Advantage:** Many records are already pre-geocoded by the State of Texas. The SODA response contains a `business_mailing` JSON object containing `type: "Point"` and `coordinates: [longitude, latitude]`. The bootstrap script extracts these coordinates directly, which eliminates the need to run Place API queries for coordinate lookups.
3.  **Database Integration:** Sanitizes business names and owner names into a clean company name, parses addresses, slugifies, and inserts the records into `texas_wells.sqlite`.

---

## Execution Commands

Ensure you are at the workspace root (`nhq-bigfoot-blueprint/`) before executing:

```bash
# Verify connection and download a sample of 5 records
python 02-workbench/water-well-drillers/scripts/texas/scratch_test_texas_api.py

# Ingest the entire Texas dataset and build the SQLite database
python 02-workbench/water-well-drillers/scripts/texas/bootstrap_texas_wells.py
```
