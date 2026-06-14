# Architect Bot Schema & Recommendations

*This document was generated from the Architect Bot response for the Water Well Drillers directory.*

## LAYER 1 — Strategic Brief

### Section 1 — What This Directory Is
A nationwide database-driven directory of water well drillers and pump maintenance specialists where every contractor has its own rich, standalone page. This platform acts as a structural, verified registry tracking state licensing data to serve rural homeowners experiencing critical water utility failures. By operating as a pure programmatic database product rather than a traditional content site, it can instantly scale across thousands of local jurisdictions.

### Section 2 — Why This Niche Wins on Google
This directory targets high-urgency, local-intent search behavior where homeowners require immediate emergency solutions. Search results today are dominated by generic regional aggregators like Yelp or Angi that lack specific industry data, rendering them highly beatable. Our directory fills this specific gap by pulling and prominently displaying active state-issued license numbers, depth capabilities, and verified certifications. An example query is "emergency well pump replacement orange county".

### Section 3 — Who Searches for This
A rural or independent homeowner whose water pressure dropped to zero on a Saturday morning, leaving their family with no running water. They are stressed, need a specialist who can work on their specific deep-well setup, and require immediate verification that the technician is licensed and trustworthy.

### Section 4 — Revenue Model
1. **Claimed Listings (MVP):** Local drilling operations pay a monthly fee to upgrade their standalone profile pages, unlock direct lead buttons, and add custom project portfolios.
2. **Email List (MVP):** A newsletter built around a "Seasonal Well Maintenance & Water Safety Checklist" lead magnet to keep users engaged during non-emergency periods.
3. **Affiliate Placements (Phase 2):** Contextual product recommendations for water filtration systems, testing kits, and backup power generators.
4. **Lead Generation (Phase 2):** Routing high-intent emergency service calls and project quotes directly to regional drilling businesses on a pay-per-lead basis.

### Section 5 — Data Sources
* **Primary Source:** Texas Water Development Board (TWDB) Submitted Driller's Reports (CSV)
* **Gap-Filler Source:** Google Maps Text Search (via Places API)

### Section 6 — MVP Definition
* **Listing count:** 2,000 listings live and indexed 
* **Quality gate:** All listings pass the anti-thin-content check before publishing 
* **Browsing:** Search, filter, and category pages work at launch 
* **Monetization:** Revenue fields exist in the schema but ship empty until Phase 2 

---

## LAYER 2 — Field Schema

### Layer 1 — Core Location and Contact (12 fields — fixed)
`listing_name`, `listing_type`, `listing_status`, `street_address`, `city`, `state`, `zip_code`, `county`, `manual_lat`, `manual_lng`, `phone_number`, `website_url`

### Layer 2 — Import Requirements (6 fields — fixed)
`post_status`, `featured`, `admin_category`, `admin_location`, `listing_img`, `date`

### Layer 3 — Domain-Specific Fields (11 fields — unique to niche)
`license_number`, `license_status`, `drilling_depth_limit`, `service_specialty`, `emergency_repair_247`, `well_casing_materials`, `pump_types_serviced`, `water_testing_offered`, `commercial_capable`, `residential_capable`, `insurance_verified`

### Layer 4 — AI Enrichment Layer (44 fields)
* **4a — listing_content (1 field):** Full HTML description, 200–400 words.
* **4b — Speakable Fields (3 fields):** `speakable_what_you_find`, `speakable_listing_details`, `speakable_quick_facts`
* **4c — Quick Facts Block (4 fields):** `quickfact_best_for`, `quickfact_primary_items`, `quickfact_fee_structure`, `quickfact_access`
* **4d — Q&A Blocks (40 fields):** 20 Q&A pairs (qa_1_question through qa_20_question and qa_1_answer through qa_20_answer) with specific domains for `well-driller` and `pump-specialist`.

### Layer 5 — Google Places Integration (12 fields — fixed)
`google_place_id`, `google_rating`, `google_review_count`, `review_1_author`, `review_1_rating`, `review_1_text`, `review_2_author`, `review_2_rating`, `review_2_text`, `review_3_author`, `review_3_rating`, `review_3_text`

### Layer 6 — Data Freshness and Tracking (5 fields — fixed)
`data_freshness`, `enriched_at`, `enrichment_source`, `data_source`, `source_id`

### Layer 7 — Monetization Fields (4 fields — fixed)
`listing_tier`, `advertiser_cta_url`, `affiliate_hook_category`, `email_optin_hook`

---

## Architectural Recommendations

### 1. Frontend Framework & Routing
**Astro** configured in hybrid or Static Site Generation (SSG) mode. Serves pure static HTML with zero client-side JavaScript by default for optimal TTFB and LCP.
**URL Structure:** `/[state]/[county]/[slug].astro`

### 2. Database & Backend
**PostgreSQL via Supabase**. 
* **Staging Schemas:** Upload raw SQLite dumps here for cleansing and AI enrichment loops.
* **Production Sync:** Transfer via atomic `UPSERT` queries.
* **Database Indexing:** Composite indexes on `(state, county)`.

### 3. Deployment & Scale
Deploy Astro on **Vercel** or **Netlify**. Use a `directory_type` column for a multi-tenant namespace strategy, allowing the same codebase and database to run the Wastewater and Propane directories in the future.
