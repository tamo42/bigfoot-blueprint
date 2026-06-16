# Phase 1: Viability Assessment - HVAC Commercial Hub

**Project ID:** 04-HVAC-HUB
**Status:** Phase 1 (Viability)
**Companion Project:** [Ambient Report](https://ambient-report.beehiiv.com/)

---

## 1. Niche Overview & Strategy

**Target Avatar:** HVAC Owner-Operators focused on commercial scaling.
**Core Value Proposition:** A high-utility, localized "rolodex" that solves two massive problems for commercial HVAC owners:
1. **Operational bottlenecks:** Finding specialized parts, sheet metal fabrication, and alternative equipment distributors quickly.
2. **Revenue growth:** Providing a localized lead list of active Commercial General Contractors and Property Management firms for bidding and maintenance contracts.
**Synergy:** Acts as the top-of-funnel acquisition magnet for the *Ambient Report* newsletter, which provides the market and pricing intelligence these exact same owners rely on.

---

## 2. Core Entities to Track

This directory will aggregate six distinct business types into a single interface:

1. **Local HVAC Supply Houses & Distributors** (Quick reference, map-based).
2. **Sheet Metal Suppliers & Specialized Dealers** (Custom fabrication, specialty metals).
3. **Commercial General Contractors (GCs)** (Lead gen for new commercial builds and fit-outs).
4. **Commercial Property Management Firms** (Lead gen for lucrative, recurring preventative maintenance contracts).
5. **Heavy Equipment & Crane Rigging Services** (Emergency alternatives when their primary crane operator is booked out).
6. **Scrap Metal Recyclers** (Quick reference for highest payout locations when recycling tear-out commodities like copper and steel).

---

## 3. Data Source Viability & Scraping Strategy

Is it possible to build a comprehensive, automated dataset for these entities?

| Entity Type | Potential Data Sources | Viability Rating | Notes |
| :--- | :--- | :--- | :--- |
| **Supply Houses & Specialty Dealers** | Google Maps/Places API, Manufacturer "Dealer Locator" pages (e.g., Trane, Carrier). | High | Low volume, static data. Easy to map. |
| **Commercial GCs** | State Licensing Boards (e.g., GA Secretary of State, State Construction Industry Licensing Boards), Dodge Construction Network (public records), Local building permits. | High | Highly structured, publicly available via state registries. |
| **Property Management Firms** | Real Estate Association member lists (e.g., BOMA, IREM), Google Places, LinkedIn. | Medium-High | Can be scraped via Maps and enriched with LinkedIn or corporate registry data for key contacts. |
| **Crane Rigging Services** | Google Maps/Places API, Specialized industry directories. | High | Highly localized. Can be scraped via Maps. |
| **Scrap Metal Recyclers** | Google Maps/Places API, Local municipal recycling registries. | High | Low volume, static data. Similar to supply houses. |

---

## 4. Search Intent Mapping & Custom Schema

Based on programmatic Keyword Research, we have mapped three distinct intents that this directory must solve:

**1. B2B Growth Intent (Contracts & Leads)**
* **Queries:** *"how to get hvac maintenance contracts"*, *"how to get commercial hvac leads"*, *"how to price hvac maintenance contracts"*
* **Solution:** A lead-gen database of Commercial GCs and Property Managers.
* **Calculator/Tool (The Reciprocity Hook):** A **"Material Cost vs. Bid Estimator"** powered by the *Ambient Report's* PPI and copper/steel pricing data to help owners accurately price these contracts.

**2. Operational / Emergency Supply Intent**
* **Queries:** *"where is the nearest hvac supply house"*, *"where to buy hvac sheet metal"*
* **Solution:** An enriched map of Supply Houses and Specialty Dealers.

### Domain-Specific Schema Requirements
To beat Google Maps and satisfy the operational intent, our database schema and web scrapers must extract the following custom columns during Phase 2/3:
- `brands_carried_oem` (e.g., Trane, Carrier, York, Lennox)
- `emergency_parts_access_24_7` (Boolean/Details on after-hours access)
- `delivery_capabilities_boom_truck` (Boolean: Do they deliver to commercial rooftops?)
- `commercial_credit_terms` (Net-30/Net-60 availability)
- `specialty_stock_commercial` (Do they stock 3-phase heavy equipment?)

---

## 5. Enrichment Strategy (The "Bigfoot" Moat)

Raw data isn't enough. We must enrich the data to make it undeniably useful.

- **For Suppliers:** Use LLMs to visit their websites and extract the domain-specific schema requirements listed above.
- **For GCs & Property Managers:** Enrich with the name of the "Chief Estimator" or "Director of Maintenance" by cross-referencing LinkedIn or company 'About Us' pages. 

---

## 6. Next Steps for Phase 2 (Data Collection)

To prove this model works without over-investing time, we should:
1. **Select a single test market:** **Atlanta, GA Metro Area**.
2. **Build Scraper 1:** Target Commercial GCs and Property Managers in Atlanta first, as this is the highest-value data for the HVAC owner.
3. **Build Scraper 2:** Map the local supply houses, specialty dealers, crane operators, and metal recyclers in Atlanta.
4. **Review Data:** Validate the dataset in `cache/` before moving to Phase 3 (Enrichment).
