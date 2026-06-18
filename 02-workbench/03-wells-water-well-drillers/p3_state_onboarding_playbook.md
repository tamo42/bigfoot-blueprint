# Phase 3: State Ingestion & Enrichment Playbook (03-Wells Project)

This playbook outlines the step-by-step pipeline for onboarding new states, consolidating them into the unified national database, enriching them using Google Places and Gemini, and deploying them to the production site.

---

## 🗺️ Execution Sequence

When onboarding a new state to the water well directory, execute these phases in exact sequence to prevent data regression and ensure complete county page coverage.

### Phase A: Raw Ingestion & Schema Check (Control Plane)
1. **Scrape State Records**: Run the state scraper (located in `02-workbench/03-wells-water-well-drillers/scripts/{state}/`) to output a clean `{state}_wells.sqlite` database in the project's `data/` directory.
2. **Schema Alignment**: Verify that the table schema matches the target `well_contractors` table exactly. Use lower-case column casing to prevent mapping failures during database consolidation.

### Phase B: Safe Relational Consolidation
1. **Consolidation Migration**: Run `p3_migrate_databases.py` (in `scripts/general/`) to compile the new national `water_well_directory.sqlite`.
2. **RESTORE Historical Enrichments**: 
   > [!IMPORTANT]
   > The migration script compiles the database from scratch and will wipe out all existing reviews, scorecards, and Q&As. You must immediately run `restore_enriched_data.py` (to restore pre-existing states' reviews and Q&As from the previous git HEAD/backup database) and `restore_florida_data.py` (to recover Florida enrichment data) before proceeding.
3. **Backfill Missing Counties**: Run `p3_enrich_counties.py` (in `scripts/general/`) to assign counties based on city-to-county lookups. *Never proceed to compilation if records lack counties, as this drops page generation counts by 4x per missing combination.*

### Phase C: Places & Gemini Enrichment with Active Monitoring
1. **Launch Scrapes & Enrichment**: Run `p3_enrich_places_apify.py` and `p3_enrich_listings.py` for the new state.
2. **Active Management & Monitoring**:
   * **Script Pacing**: Ensure the Gemini scripts use thread-locked rate limit pacing (1.0s throttle) to prevent `429` rate limit blockages.
   * **Active Logs**: Ensure all scripts print timestamped progress logs.
   * **Stall Monitors**: Set timers at **50%, 100%, and 125%** of the expected run time to inspect the log files. If progress has halted or retries are looping, terminate the process and run in a smaller batch limit.

### Phase D: Deployment & Build Verification
1. **Stage to Production**: Copy the fully consolidated and enriched database to `uswelldrillers.com/src/data/water_well_directory.sqlite`.
2. **Run Static Build**: Execute `npm run build` in the website directory.
3. **Automated Content Audit**: Run `verify_pages.py` (in `uswelldrillers.com`) to sample 10 counties per state. Assert that:
   * **Status OK**: 100% of pages are successfully built.
   * **Schema JSON-LD**: Present on all pages.
   * **Listings & Scores**: Active listing cards and Gemini scorecards (where reviews exist) render correctly.
   * **Maps & EPA Alerts**: Maps and health violation blocks are active.
4. **Git Commit & Push**: Stage, commit, and push both the control plane and website changes to finalize tracking.
