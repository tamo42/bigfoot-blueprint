# Project: Georgia Real Estate & Closing Attorneys Directory

This workbench folder serves as the central context and design registry for the **Georgia Closing Attorneys** directory. 

---

## 1. Project Overview & Strategy
* **Niche**: Real Estate Closing Attorneys and Title/Escrow Agents in the State of Georgia.
* **Directory Family**: **People** (Licensed Attorneys, Law Firms).
* **Target Audience**: Home buyers, home sellers, real estate agents, loan officers, and real estate investors.
* **Core Value Proposition**: Georgia is an "attorney state" (real estate closings must be conducted under the supervision of a licensed Georgia attorney). This directory aggregates all licensed real estate closing attorneys, verifying their active bar standing, county coverage, and title insurance appointments.

---

## 2. Success Triggers (Stage 1 to Stage 2 Lifecycle)
In alignment with the [bigfoot-blueprint-framework.md](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/source/bigfoot-blueprint-framework.md#L157-L176), the project starts on Stage 1 (Static Vercel Hosting + SQLite local database) and will be migrated to Stage 2 (Dynamic Supabase integration) when either of these triggers is met:
* **The Engagement Trigger**: A minimum of 2 organic "Claim my Listing" inquiries or contact form submissions.
* **The Traffic Trigger**: Achieves 500+ search impressions and 20+ organic clicks per week in Google Search Console for three consecutive weeks.

---

## 3. High-Leverage Prompt Context
The prompt used to architect the schema in the **Directory Intelligence (Architect)** Gem is saved here for reference:

```markdown
Role: You are the Directory Intelligence (Architect) bot, designed to help build database-driven niche directories that rank on Google and provide structured feeds for AI search engines. 

Niche Concept: Georgia Real Estate & Closing Attorneys Directory (focused on residential and commercial real estate attorneys, title agents, and escrow services).
Target Audience: Home buyers, sellers, real estate agents, lenders, and investors seeking closing attorneys.
Directory Family: "People" (licensed professionals, law firms, and credentials).

Please architect a comprehensive programmatic directory blueprint for this niche in Markdown format (.md) that follows the Bigfoot Blueprint Framework.
```

The detailed strategic brief and database field schemas returned by the Gem are documented in [architect-schema.md](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/01-gabar-georgia-closing-attorneys/architect-schema.md).
The engineering specifications, question selections, code assets, and deployment guides for the Apify scraper/enricher are tracked in [pipeline-spec.md](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/01-gabar-georgia-closing-attorneys/pipeline-spec.md).

Data Extraction and Ingestion Assets:
- [fetch-seed-direct.py](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/01-gabar-georgia-closing-attorneys/fetch-seed-direct.py): Python script that queries GABAR's internal web API directly in paginated batches of 500, pulling only Georgia attorneys belonging to the Real Property Law section (`REALP19`). This completely bypasses Apify and completes in under 5 minutes.
- [fetch-seed.py](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/01-gabar-georgia-closing-attorneys/fetch-seed.py): Python script that triggers the GABAR member scraper on Apify, polls for completion, and downloads the raw seed CSV data automatically.
- `01-gabar-georgia-closing-attorneys_seed.csv` (target): Raw seed data containing licensed attorneys.

---


## 4. Initial Database Schema Specs
The SQLite database (`directory.sqlite`) will contain the following primary tables:

### A. `attorneys`
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Unique primary key |
| `first_name` | TEXT | First name |
| `last_name` | TEXT | Last name |
| `bar_number` | TEXT (Unique) | State Bar of Georgia registration number |
| `license_status` | TEXT | Bar license status (e.g., Active, Inactive, Disbarred) |
| `admission_date` | TEXT | Date admitted to the Georgia Bar |
| `disciplinary_history` | TEXT | Regulatory discipline logs or "None" |
| `firm_name` | TEXT | Registered law firm name |
| `office_address` | TEXT | Physical office address |
| `city` | TEXT | City |
| `county` | TEXT | Primary office county |
| `zip_code` | TEXT | Zip code |
| `latitude` | REAL | Map coordinate latitude |
| `longitude` | REAL | Map coordinate longitude |
| `phone` | TEXT | Office phone number |
| `email` | TEXT | Contact email |
| `website_url` | TEXT | Website URL |
| `coi_verified` | INTEGER (Boolean) | Certificate of Insurance presence (0/1) |
| `coi_limits` | TEXT | E&O/Liability limits description |
| `appointments` | TEXT | JSON/CSV of appointed title underwriters (e.g., Chicago Title, First American, Fidelity) |
| `specialties` | TEXT | JSON/CSV of specialties (e.g., Commercial, Double Closings, Probate) |
| `faq_enriched` | TEXT | JSON string of the Top 20 Q&A answers (Gemini-enriched) |
| `claimed` | INTEGER (Boolean) | Listing claim status (0/1) |

---

## 5. Free Reciprocity Asset: Closing Cost & Seller Net Sheet
* **Tool Objective**: Above-the-fold interactive calculator.
* **Functionality**:
  * Seller enters Sales Price, Mortgage Payoff, and County.
  * Calculator instantly outputs estimated Georgia Transfer Tax ($1 per $1,000 of sales price), County Recording Fees, Title Search/Insurance Estimates, and Estimated Closing Attorney fee.
  * Direct Call-to-Action: *"You have $X estimated closing costs. Connect with local, bar-verified closing attorneys in [County] to lock in your closing."*
