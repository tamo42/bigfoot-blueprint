# Version 2 Expansion Roadmap: Georgia Closing Lawyers

**Objective:** Transition the MVP directory into the undisputed authoritative source for real estate legal data in Georgia by aggregating multi-dimensional public, private, and peer-reviewed data sources.

## Phase 1: The "Aggregated Authority" Layer
*Goal: Provide immediate social proof and mathematically rank our "Best Of" pages.*

1. **Google Maps Reviews (Via Apify)**
   - **Action:** Run the `compass/crawler-google-places` Apify actor across our existing database of 2,220 attorneys (matching on firm name and address).
   - **Data Extracted:** Google Rating (Stars), Total Review Count, precise opening hours, and top positive/negative reviews.
   - **Implementation:** Use this data to algorithmically sort the statewide directory and inject valid `AggregateRating` schema into the profiles to capture gold stars in SERPs.

2. **Legal Directory Peer Metrics (Avvo / Justia)**
   - **Action:** Scrape Avvo and Justia profiles using established Apify actors.
   - **Data Extracted:** "Avvo Rating", peer endorsements, and disciplinary flags (as a secondary check to GaBar data).
   - **Implementation:** Display an "Aggregated Trust Score" that combines Google, Avvo, and State Bar standing into a single, easy-to-read metric for consumers.

## Phase 2: The "Investor Intel" Layer
*Goal: Offer proprietary, high-value data that no other legal directory (like Justia or Avvo) can provide, specifically targeting the investor avatar.*

1. **Transaction Volume Validation (Via DataTree)**
   - **Action:** Leverage the existing DataTree subscription to ingest and cross-reference county deed records.
   - **Data Extracted:** The name of the closing attorney or settlement firm recorded on the deed/settlement statement.
   - **Implementation:** Calculate the actual closing volume for attorneys in specific counties. Award verified badges (e.g., "Top 1% Closing Volume in Fulton County" or "Verified: 150+ Closings in 2025"). This is the ultimate trust signal for investors.

2. **Secretary of State (SOS) Registered Agent Data**
   - **Action:** Scrape or query the Georgia SOS business registry.
   - **Data Extracted:** Attorneys acting as the "Registered Agent" for real estate holding companies (LLCs).
   - **Implementation:** Identify attorneys who represent a high volume of LLCs. Tag these profiles as "Investor-Friendly Veterans" or "Commercial Setup Specialists," directly answering the intent of wholesale and commercial buyers.

## Phase 3: The "Litigation & Defense" Layer
*Goal: Prove an attorney's courtroom capability for distressed property, quiet title, and zoning disputes.*

1. **Court Dockets & Litigation History (Via UniCourt or CourtListener)**
   - **Action:** Query legal APIs using the attorney's Georgia Bar Number.
   - **Data Extracted:** Active and historical court cases, specifically filtering for real estate, eviction, or property dispute dockets.
   - **Implementation:** Display metrics like "Active Cases in Superior Court" or "Recent Evictions Handled." This transitions the directory from a simple list to a verified resume of an attorney's fighting capability.

## Next Steps
- Establish the data pipeline to match Apify outputs back to the primary SQLite database via `gabar_id` or fuzzy name/address matching.
- Upgrade the Astro frontend to conditionally render the new data layers (badges, star ratings, case counts) as the data becomes available.
