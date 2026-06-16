# Bigfoot Blueprint Niche Project: Mobile Loan Signing Agents

## 1. Project Overview & The "Why"

**Target Niche:** Mobile Notaries & Loan Signing Agents
**Avatar:** Title Companies, Real Estate Investors, Law Firms
**Strategic Adjacency:** This directory directly cross-pollinates with our existing **Georgia Closing Lawyers** directory. The same avatar who needs a closing attorney often needs a mobile notary for out-of-state sellers, mail-aways, or after-hours closings.

Traditional notary directories are just thin name-and-number lists. We are building an *enriched* directory focused specifically on **Loan Signing Agents (LSA)**. By highlighting their E&O insurance limits, NNA background check status, and precise mobile service radiuses, we provide instant trust for high-stakes real estate transactions.

### The Curated Moat
We will combine multiple disparate data feeds to create a defensible asset:
* State Secretary of State (SOS) Commission Registries
* National Notary Association (NNA) Certifications / Background Checks
* Geolocation API (for mobile service area polygons)

---

## 2. The Reciprocity Tool (Hormozi Playbook)

To provide immediate, un-gated value before asking for claims or leads, we will feature a **Legal Travel Fee & Notary Cost Calculator** on the primary viewport.

* **How it works:** The user inputs their state, the number of signatures required, and the estimated travel distance for the notary.
* **The Value:** The calculator outputs the exact maximum fee allowed by that specific state's laws (e.g., "$5 per signature + $0.50/mile"). 
* **The Conversion:** This instantly validates the expected cost for the buyer and leads directly into a frictionless CTA: *"Find Top-Rated Mobile Notaries within your travel radius."*

---

## 3. The 48-Hour Workflow (Rodrigo's Pipeline)

This project follows the strict Bigfoot Blueprint 48-Hour Pipeline to maintain $0/month bootstrapping costs.

### Phase 1: Keyword Research & Intent Mapping
* **Action:** Run programmatic queries using the AnswerThePublic Python script (`02-workbench/answerthepublic/scripts/fetch-atp.py`) to extract real search volume for "mobile notary" and "loan signing agent".
* **Goal:** Identify the top 10-20 questions users ask (e.g., "Can a mobile notary come to a hospital?", "How much does a loan signing agent charge?"). 
* **Deliverable:** A `p1_intent_manifest.md` document outlining the custom database schema fields we need to capture (e.g., `has_hospital_clearance`, `max_travel_radius`).

### Phase 2: Data Extraction & Cleaning
* **Action:** Scrape the initial seed data. Target 1 or 2 specific states first (e.g., Texas, Florida, or Georgia) via their Secretary of State public notary search portals.
* **Focus:** Filter the data to focus on *mobile* notaries or *loan signing agents*—not just standard UPS store clerks.
* **Deliverable:** A raw, cleaned CSV or JSON file containing Name, City, Phone, Commission Number, and commission expiration dates.

### Phase 3: Programmatic LLM Enrichment
* **Action:** Feed the raw listings through the Gemini 2.5 model natively in the Antigravity IDE (via Python scripting).
* **Prompt Logic:** Have Gemini generate deep, conversational answers to the "Top 20 Questions" (from Phase 1) for *each specific notary profile*. This builds the massive "thin content" armor required to rank.
* **Deliverable:** A finalized `directory.sqlite` database file with deep, schema-rich data for every listing.

### Phase 4: Astro + SQLite Git Build
* **Action:** Inject the `directory.sqlite` file into our standardized Astro static site template.
* **Routing Constraints:** 
  * Flat structure for hubs: `domain.com/atlanta-05-notaries-mobile-notaries`
  * Flat structure for listings: `domain.com/atlanta-john-doe-notary`
* **Performance Goal:** Zero client-side JS (except the calculator). 100/100 Lighthouse score. 
* **Schema Goal:** Ensure `JSON-LD` schemas (`LocalBusiness`, `Person`, `FAQPage`, and `Speakable`) are injected programmatically on build so AI engines (Perplexity/ChatGPT) can scrape us efficiently.

### Phase 5: Edge Deploy (Stage 1 Validation)
* **Action:** Commit the codebase and SQLite file to a private GitHub repo and auto-deploy it via Vercel or Netlify.
* **Success Metric:** Once live, the site sits in Stage 1 ($0/month hosting). We will monitor Google Search Console. If it hits **>60% indexing** or receives **3 organic profile claim requests**, it passes the gate and we upgrade it to Stage 2 (Supabase multi-tenant).

---

## 4. Next Steps for Rodrigo

1. **Review & Align:** Read through this brief and ensure you understand the Avatar (Real Estate Investors/Title Companies) and the specific Moat we are building.
2. **Execute Phase 1:** Navigate to `02-workbench/answerthepublic/scripts/` and run `fetch-atp.py` for "mobile notary" and "loan signing agent". Save the output and draft the `p1_intent_manifest.md` inside a new `02-workbench/05-notaries-mobile-notaries/` folder.
3. **Target Selection:** Identify the easiest state registry (e.g., Florida SOS) to build your first Phase 2 data scraper.
