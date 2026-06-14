# Georgia Water Well Contractors Ingestion Runbook

This directory handles harvesting, parsing, and deduplicating water well drillers and pump installers for the State of Georgia.

---

## Data Source

*   **Agency:** Georgia Environmental Protection Division (EPD)
*   **Source Format:** PDF Rosters
*   **Original URL:** [Georgia EPD Water Well Standards](https://epd.georgia.gov)
*   **Cached Source PDFs:**
    *   `cache/georgia_licensed_water_well_contractors.pdf`
    *   `cache/georgia_certified_pump_contractors.pdf`
    *   `cache/georgia_bonded_drilling_contractors_pg_pe.pdf`

---

## Technical Extraction Process

The Georgia registries are published as formatted tables in separate PDFs. The extraction pipeline works as follows:

1.  **Layout Reading:** Page text is extracted using `pypdf`'s layout mode, preserving space-separated columns.
2.  **Regex Column Splitting:** Lines are split using regex pattern `\s{2,}` (double spaces or more) to isolate license numbers, company names, street addresses, cities, states, and zip codes.
3.  **Deduplication:** Listings are consolidated across all three PDFs by checking for unique combinations of `Company Name` and `City`. If a company holds multiple licenses (e.g., both a driller and pump installer license), they are merged into a single database profile, and the license codes are appended as a comma-separated list.
4.  **Google Places API Enrichment:** The consolidated list is resolved against Google Maps details to capture websites, latitude/longitude, ratings, and user reviews.

---

## Execution Commands

Ensure you are at the workspace root (`nhq-bigfoot-blueprint/`) before executing:

```bash
# 1. Parse raw PDFs and bootstrap the database
python 02-workbench/water-well-drillers/scripts/georgia/bootstrap_georgia_wells.py

# 2. Enrich missing place details (using either state script or general enricher)
python 02-workbench/water-well-drillers/scripts/general/enrich_places_general.py --state georgia --limit 150
```
