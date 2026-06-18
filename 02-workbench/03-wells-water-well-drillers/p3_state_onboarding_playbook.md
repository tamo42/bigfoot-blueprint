# Phase 3: State Ingestion & Enrichment Playbook (03-Wells Project)

This playbook outlines the step-by-step pipeline for onboarding new states, consolidating them into the unified national database, enriching them using Google Places and Gemini, and deploying them to the production site.

---

## 🗺️ Execution Sequence

When onboarding a new state to the water well directory, execute these phases in exact sequence to process the data safely in isolation before merging it with the production database.

### Phase A: Raw Ingestion & Schema Alignment
1. **Scrape State Records**: Run the state scraper (located in `02-workbench/03-wells-water-well-drillers/scripts/{state}/`) to output a clean `{state}_wells.sqlite` database in the project's `data/` directory.
2. **Schema Alignment**: Verify that the columns and table casing in `{state}_wells.sqlite` match the target `well_contractors` database schema exactly (using lower-case column names) so it can be appended later without mapping errors.

### Phase B: Local Enrichment & County Mapping (In Isolation)
Perform all enrichment tasks directly on the isolated state database (`{state}_wells.sqlite`) first:
1. **Google Places & Reviews**: Run `p3_enrich_places_apify.py` targeting `{state}_wells.sqlite` to pull reviews, ratings, lat/lng coordinates, and address info.
2. **Website Crawling & Content Enrichment**: Crawl websites, then run `p3_enrich_listings.py` (with thread-locked rate limit pacing) on the state database to generate custom descriptions and Q&As.
3. **Gemini Review Analysis**: Run `p4_enrich_reviews_gemini.py` on the state database to calculate the Driller Scores from Google reviews.
4. **Local County Resolution**: Run `p3_enrich_counties.py` targeting `{state}_wells.sqlite` to map cities to counties before merging, preventing dynamic route generation failures.
5. **Active Monitoring**: During enrichment runs, monitor timestamped progress logs. Set monitors at **50%, 100%, and 125%** of the expected execution time to handle API stalls or retry loops.

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

### 2. Monitoring & Override Thresholds
Set timers at **50%, 100%, and 125%** of the calculated TTC. If execution logs diverge from these benchmarks, execute the corresponding action:

| Benchmark | Expected Milestone | Status Check / Override Actions |
| :--- | :--- | :--- |
| **50% of TTC** | Apify Places search completed; crawled text files cached; Gemini Q&A loops initiated. | **Verify Logs**: Confirm `apify_raw_dataset_*.json` is created in `/cache` and `crawled_text/` has file updates. If 0 crawls are cached, check network settings. |
| **100% of TTC** | Gemini listing enrichment complete; Gemini review scorecards (Driller Scores) complete. | **Verify DB**: Open the state SQLite database. If `qa_1_question` count is $< 80\%$ of expected website-eligible records, the Gemini worker pool has stalled. |
| **125% of TTC** | Database consolidated, appended, build complete, sitemap generated. | **Hard Stop / Manual Override**: If the script has not exited, **something is wrong** (e.g., SQLite connection lock, API quota soft block, or infinite retry loops). **Kill the process immediately**, review the logs, and rerun in a smaller batch size (`--limit`). |


