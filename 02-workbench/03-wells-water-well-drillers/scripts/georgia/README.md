# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_bootstrap_georgia_wells.py`
*   **What it does:** This script parses PDF documents from the Georgia Environmental Protection Division (EPD) containing lists of licensed well drillers, certified pump contractors, and bonded drilling contractors. It extracts contractor names, addresses, license numbers, and types. It then deduplicates this information, enriches each unique company's data with details from the Google Places API (like website, coordinates, rating, and reviews), and finally stores the structured data into a SQLite database.
*   **Why it does it:** It processes publicly available PDF documents to create a structured, searchable, and enriched database of Georgia's well drilling and pump installation service providers. This centralized database can then be used for applications requiring access to this contractor information, such as mapping services, search tools, or further analysis.
*   **Inputs:**
    *   `georgia_licensed_water_well_contractors.pdf`: A PDF file listing licensed well drillers, expected in the `cache` directory.
    *   `georgia_certified_pump_contractors.pdf`: A PDF file listing certified pump contractors, expected in the `cache` directory.
    *   `georgia_bonded_drilling_contractors_pg_pe.pdf`: A PDF file listing bonded drilling contractors, expected in the `cache` directory.
    *   `GOOGLE_PLACES_API_KEY`: An API key loaded from a `.env` file, required for Google Places API queries.
    *   `places_cache.json`: An optional local cache file for Google Places API responses.
*   **Outputs:**
    *   `georgia.db`: A SQLite database file containing a table named `installers_haulers` populated with parsed and enriched contractor data. This includes company names, addresses, contact info, Google Places details (website, rating, coordinates), and associated license types.
    *   `places_cache.json`: An updated local cache file containing responses from the Google Places API for queried companies.
    *   Standard output: Progress messages and error logs during parsing, deduplication, API enrichment, and database saving.

### `p2_complete_georgia_wells_enrichment.py`
*   **What it does:** Enriches Georgia well installer/hauler records in a SQLite database with Google Places API data (e.g., place ID, website, rating, coordinates, reviews). It uses a local cache for API responses and extracts individual review texts from the fetched JSON into separate database columns.
*   **Why it does it:** To complete and enhance the `installers_haulers` dataset by adding comprehensive public information from Google Places for records missing this data, thereby improving data quality and utility for further analysis or presentation.
*   **Inputs:**
    *   `GOOGLE_PLACES_API_KEY` environment variable (loaded from `.env` file).
    *   SQLite database (e.g., `georgia.db`) containing an `installers_haulers` table with `id`, `name`, and `city` columns.
    *   `places_api_cache.json` file (if it exists) for caching Google Places API responses.
    *   Google Places API (Find Place from Text and Place Details endpoints).
*   **Outputs:**
    *   Updated SQLite database (`georgia.db`), specifically the `installers_haulers` table, with enriched data: `google_place_id`, `website_url`, `google_rating`, `google_review_count`, `manual_lat`, `manual_lng`, `reviews_json`, `review_1_text`, `review_2_text`, and `review_3_text`.
    *   Updated or created `places_api_cache.json` file with new Google Places API responses.
    *   Console output detailing progress, cache hits, API queries made, and records updated.