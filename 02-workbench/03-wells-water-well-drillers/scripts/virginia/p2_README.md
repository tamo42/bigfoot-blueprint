# Virginia Water Well Contractor Extraction

## Overview
This folder contains scripts to extract and process water well contractors (Water Well System Providers and Contractors with WWS specialties) from the Virginia Department of Professional and Occupational Regulation (DPOR) master contractor registry.

## Data Source
- **Primary Source:** The DPOR Regulant List text file (`2705b__crnt.txt`) located at `https://www.dpor.virginia.gov/sites/default/files/Records%20and%20Documents/Regulant%20List/2705b__crnt.txt`.
- **License Board:** Virginia Board for Contractors.

## Extraction and Processing Flow
1. **Inspection:** Run `python p2_inspect_virginia.py` to stream and inspect the first 100 lines of the DPOR text file. This defines the column layouts, delimiters, and encoding (e.g. `windows-1252` or `utf-8`).
2. **Download & Parser Script:** Run `python p2_scrape_virginia.py` which:
   - Streams the text dump directly to the local cache if not already cached.
   - Decodes and parses the file line-by-line using Python streaming generators to keep memory usage near zero.
   - Filters for active licensees under the `Water Well System Provider` (WWSP) and relevant contractor specialties.
   - Normalizes names, phone numbers, and addresses.
   - Inserts or updates the records in the SQLite database (`virginia_wells.sqlite`).
3. **Google Places Enrichment:** Run the general place enricher to lookup Place ID, rating, review count, and reviews.
