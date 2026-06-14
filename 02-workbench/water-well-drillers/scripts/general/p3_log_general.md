# General Workbench Scripts

This directory contains reusable, state-agnostic Python scripts and utility modules. They are designed to prevent code duplication, enforce database schema consistency, and provide a single entry point for API data enrichment.

---

## Files

1.  **[utils.py](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/water-well-drillers/scripts/general/utils.py)**
    *   **Purpose:** Shared helpers for cleaning data and locating files.
    *   **Functions:**
        *   `get_workspace_root()`: Dynamically finds the root of the Git repo (5 directories up from this script).
        *   `resolve_path(rel_path)`: Resolves any subpath relative to the root.
        *   `slugify(text)`: Standards-compliant URL slug generator.
        *   `clean_phone_number(num)`: Normalizes phone inputs to `(XXX) XXX-XXXX`.
        *   `load_env_api_key()`: Loads the Places API key from `.env` in the root.
        *   `get_places_cache_path()`: Resolves the cache path `cache/places_cache.json`.
        *   `get_db_path(state)`: Resolves `02-workbench/water-well-drillers/data/{state}_wells.sqlite`.

2.  **[schema.py](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/water-well-drillers/scripts/general/schema.py)**
    *   **Purpose:** Defines the canonical SQLite table schema (`installers_haulers`) and manages incremental column migrations dynamically.
    *   **Usage:**
        ```python
        import schema
        schema.initialize_database("path/to/my_state.sqlite")
        ```

3.  **[enrich_places_general.py](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/water-well-drillers/scripts/general/enrich_places_general.py)**
    *   **Purpose:** Connects to any state SQLite database, inspects the table, and queries Google Places details for matched records up to a configurable safety limit.
    *   **Execution:**
        ```bash
        # Enrich Ohio database using default limit (100 Find Place queries)
        python 02-workbench/water-well-drillers/scripts/general/enrich_places_general.py --state ohio

        # Enrich Georgia database with specific safety limit
        python 02-workbench/water-well-drillers/scripts/general/enrich_places_general.py --state georgia --limit 50

        # Specify database path directly
        python 02-workbench/water-well-drillers/scripts/general/enrich_places_general.py --state Texas --db 02-workbench/water-well-drillers/data/texas_wells.sqlite --limit 150
        ```

---

## Adding a New State to the Registry

When scraping a new state's contractors:
1.  Initialize the database using `schema.initialize_database(db_path)`.
2.  Parse the raw source data (HTML, PDF, or API) and insert the records into the database. Make sure to call `utils.slugify()` to build slugs and `utils.clean_phone_number()` to normalize phones.
3.  Run `enrich_places_general.py` targeting the new state to retrieve geographic coordinates, websites, Google ratings, and reviews.
