# North Carolina Water Well Drillers Extraction

## Overview
This folder contains the extraction and processing script for the North Carolina Department of Health and Human Services (NCDHHS) well contractors registry.

## Data Source
- **Primary Source:** CSV export downloaded from the [Find a Certified Well Contractor](https://www.dph.ncdhhs.gov/programs/environmental-health/north-carolina-well-contractors-certification/find-certified-well-contractor) page. The live NCDHHS portals (`ehs.ncpublichealth.com` and `www.ncwelldriller.org`) were returning SSL and timeout errors from automated bots.
- **Rules and Statutes Bookmark:** [North Carolina Well Contractors Certification Rules and Statutes](https://www.dph.ncdhhs.gov/programs/environmental-health/north-carolina-well-contractors-certification/rules-and-statutes)

## Process
1. **Extraction Script:** `scrape_north_carolina.py` reads the CSV, parses and cleans the phone numbers, aggregates individual certified personnel and authorized services by employer, and loads them into a local SQLite database (`north_carolina_wells.sqlite`).
2. **Data Structure:** 
   - `listing_content` aggregates all certified individuals and their specific service capabilities (e.g., Well Construction, Pump Install/Repair).
3. **Enrichment:** `enrich_places_general.py` runs over the SQLite DB to append Google Places data (Ratings, Reviews, Lats/Longs) for the aggregated companies.

## Technical Challenges
- The provided CSV had `windows-1252` encoding (containing the `0xa0` byte).
- Some CSV records didn't have a distinct "Employer". For those, we fallback to treating the individual contractor name as the company name.
- The `city` field was absent in the CSV (only County and State were provided), which required updating the `enrich_places_general.py` to handle `None` gracefully during place queries.
