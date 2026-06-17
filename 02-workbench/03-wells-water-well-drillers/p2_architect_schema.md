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

### Layer 3 — Domain-Specific Fields (30 fields — unique to niche)
`license_number` (State-issued license number),
`license_type` (Specific contractor designation),
`license_status` (Active/Expired/Suspended),
`licensing_agency` (State licensing authority),
`emergency_repair_247` (Boolean flag),
`emergency_response_time` (Typical emergency window),
`emergency_services_offered` (JSON or list of emergency repairs),
`service_radius_miles` (Max travel distance),
`served_counties` (Comma-separated list of counties),
`drilling_depth_limit` (Depth capability),
`drilling_methods_available` (e.g., Air Rotary, Mud Rotary, Cable Tool),
`drilling_diameters` (Casing sizes handled),
`geological_specialties` (Formation expertise),
`well_rehabilitation_offered` (Yield restoration techniques),
`pump_types_serviced` (Submersible, Jet, Constant Pressure/VFD, Solar, Hand),
`pump_brands_serviced` (Grundfos, Franklin Electric, Goulds, Pentair),
`pressure_tank_services` (Boolean flag),
`water_testing_offered` (Boolean flag),
`water_contaminants_tested` (Bacteria, Lead, PFAS, Nitrates, etc.),
`water_treatment_installed` (Water softeners, UV, RO systems),
`residential_capable` (Boolean flag),
`commercial_capable` (Boolean flag),
`bonded_insured_details` (Liability limits & surety bond info),
`payment_methods_accepted` (Cash, Check, Credit, Financing),
`financing_available` (Boolean flag),
`accepts_usda_rural_grants` (Boolean flag for Section 504),
`wells_drilled_last_5_years` (Verified count from state well logs),
`average_well_depth_ft` (Derived from well logs),
`average_yield_gpm` (Derived from well logs),
`local_epa_water_alerts` (JSON/List of EPA contamination alerts in service area)

### Layer 4 — AI Enrichment Layer (28 fields)
* **4a — listing_content (1 field):** Full HTML description, 200–400 words.
* **4b — Speakable Fields (3 fields):** `speakable_what_you_find`, `speakable_listing_details`, `speakable_quick_facts`
* **4c — Quick Facts Block (4 fields):** `quickfact_best_for`, `quickfact_primary_services`, `quickfact_pricing_guide`, `quickfact_service_area`
* **4d — Q&A Blocks (20 fields):** 10 Q&A pairs (qa_1_question through qa_10_question and qa_1_answer through qa_10_answer) covering:
  1. Emergency/Weekend Response Details (urgency/rates)
  2. Local permit filing and state regulatory procedures (compliance)
  3. Well casing setback requirements from septic/sewer lines (safety)
  4. Local groundwater/aquifer depth and water level details (geological context)
  5. Water testing services and filtration systems offered (health)
  6. Warranty on pumps, tanks, and labor (financial assurance)
  7. Well rehabilitation methods for dry/low water yield wells (repaired status)
  8. Solar/Off-grid pumping capability and battery backup installation (alternate power)
  9. Well abandonment/decommissioning services (legal closure of old wells)
  10. Payment terms, credit cards, or financing options available (convenience)


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
