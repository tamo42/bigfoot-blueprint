# Phase 3: State Ingestion & Enrichment Playbook (03-Wells Project)

This playbook outlines the step-by-step pipeline for onboarding new states, consolidating them into the unified national database, enriching them using Google Places and Gemini, and deploying them to the production site.

---

## 🗺️ Execution Sequence

When onboarding a new state to the water well directory, execute these phases in exact sequence to process the data safely in isolation before merging it with the production database.

### Phase A: Raw Ingestion & Schema Alignment
1. **Scrape State Records**: Run the state scraper (located in `02-workbench/03-wells-water-well-drillers/scripts/{state}/`) to output a clean `{state}_wells.sqlite` database in the project's `data/` directory.
2. **Schema Alignment**: Verify that the columns and table casing in `{state}_wells.sqlite` match the target `well_contractors` database schema exactly (using lower-case column names) so it can be appended later without mapping errors.

### Phase B: Local Enrichment & County Mapping (In Isolation)
Perform all enrichment tasks directly on the isolated state database (`{state}_wells.sqlite`) first, invoking the scripts from the repository root:
1. **Google Places & Reviews**: Run the Apify Place matching script to pull reviews, ratings, lat/lng coordinates, and website URLs:
   ```bash
   python scripts/p3_enrich_places_apify.py --db 02-workbench/03-wells-water-well-drillers/data/{state}_wells.sqlite --state {state}
   ```
2. **Website Crawling**: Run the local crawl script to download and cache text content from the matched website URLs:
   ```bash
   python 02-workbench/03-wells-water-well-drillers/scripts/general/p3_crawl_websites.py --db 02-workbench/03-wells-water-well-drillers/data/{state}_wells.sqlite
   ```
3. **Gemini Listing Enrichment**: Run the Gemini listing enricher to parse cached crawled text and populate custom HTML descriptions and Q&As:
   ```bash
   python 02-workbench/03-wells-water-well-drillers/scripts/general/p3_enrich_listings.py --db 02-workbench/03-wells-water-well-drillers/data/{state}_wells.sqlite --mode full
   ```
4. **Gemini Review Analysis**: Run the scorecard generator to calculate overall Driller Scores from Google reviews:
   ```bash
   python scripts/p4_enrich_reviews_gemini.py --db 02-workbench/03-wells-water-well-drillers/data/{state}_wells.sqlite
   ```
5. **Local County Resolution**: Run the county backfiller to resolve city-to-county mappings before merging:
   ```bash
   python 02-workbench/03-wells-water-well-drillers/scripts/general/p3_enrich_counties.py --db 02-workbench/03-wells-water-well-drillers/data/{state}_wells.sqlite
   ```
6. **Active Monitoring**: During enrichment runs, monitor timestamped progress logs. Set monitors at **50%, 100%, and 125%** of the expected execution time to handle API stalls or retry loops.


### Phase C: Append to Unified Database
1. **Append State Table**: Run the database append script to relationally merge the completed, fully enriched records and technician licenses from the state database (`{state}_wells.sqlite`) directly into the master `water_well_directory.sqlite`:
   ```bash
   python 02-workbench/03-wells-water-well-drillers/scripts/general/p3_append_state_database.py --state-db 02-workbench/03-wells-water-well-drillers/data/{state}_wells.sqlite
   ```
2. **Verify Masters**: Assert that the main database has not modified or lost any pre-existing records for other states, and that the new state records are fully appended with their reviews, scorecards, and Q&As intact.

### Phase D: Deployment & Build Verification
1. **Stage to Production**: Copy the updated unified database to `uswelldrillers.com/src/data/water_well_directory.sqlite`.
2. **Run Static Build**: Execute `npm run build` in the website directory.
3. **Automated Content Audit**: Run `verify_pages.py` to sample 10 counties per state and confirm all features (JSON-LD schema, listings, Driller Scores, EPA data, and map iframes) are rendering correctly.
4. **Git Commit & Push**: Stage, commit, and push changes in both repositories to finalize tracking.

---

## ⏱️ Time to Completion (TTC) Benchmarking & Active Monitoring

Before launching the enrichment pipeline, calculate the expected execution baseline using the formulas below. Use this baseline to configure automated monitors and trigger active overrides if performance deviates.

### 1. Baseline Projection Formula
Map the workload using the primary variables from the state dataset:
* $R$: Number of raw regulatory database/completion log records.
* $V$: Number of target drilling vendors (companies).
* $W$: Crawlable website ratio (percentage of vendors with crawlable sites; baseline $\approx 50\%$ or $0.5$).
* $K$: Review scorecard ratio (percentage of vendors with Google reviews; baseline $\approx 30\%$ or $0.3$).

$$\text{Projected TTC (seconds)} = (R \times 0.001) + V \times [0.5 + 1.25W + 1.0K] + T_{\text{build}} + 145$$

*Note: $T_{\text{build}} \approx 15\text{s} + (\text{Total Pages} / 600)$.*

### 2. Two-Level Monitoring & Override Thresholds
Set active monitoring timers at **50%, 100%, and 125%** of the expected duration at both the **individual batch level** (within each stage) and the **overall pipeline level** (for the entire state onboarding process).

#### A. Batch-Level Monitoring (Within Individual Stages)
For each batch size $B$ passed to a script (e.g. Apify search, crawl, or Gemini run):
* **50% of Batch TTC**: Check that the script's log output shows active processing (e.g. at least 25% of queries have successfully returned).
* **100% of Batch TTC**: Check that the database updates or cache writes match the batch count. If updates are $< 80\%$, the threads are throttling or blocked.
* **125% of Batch TTC (Hard Stop)**: If the batch loop is still running, kill it immediately to prevent infinite retries.

#### B. Overall Pipeline Monitoring (Master Process)
For the calculated master TTC across the entire state ingestion:

| Benchmark | Expected Milestone | Status Check / Override Actions |
| :--- | :--- | :--- |
| **50% of Master TTC** | Apify Places search completed; crawled text files cached; Gemini Q&A loops initiated. | **Verify Logs**: Confirm `apify_raw_dataset_*.json` is created in `/cache` and `crawled_text/` has file updates. If 0 crawls are cached, check network settings. |
| **100% of Master TTC** | Gemini listing enrichment complete; Gemini review scorecards (Driller Scores) complete. | **Verify DB**: Open the state SQLite database. If `qa_1_question` count is $< 80\%$ of expected website-eligible records, the Gemini worker pool has stalled. |
| **125% of Master TTC** | Database consolidated, appended, build complete, sitemap generated. | **Hard Stop / Manual Override**: If the script has not exited, **something is wrong** (e.g., SQLite connection lock, API quota soft block, or infinite retry loops). **Kill the process immediately**, review the logs, and rerun in a smaller batch size (`--limit`). |



