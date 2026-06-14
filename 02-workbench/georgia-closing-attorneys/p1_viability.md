# Phase 1: Niche Discovery & Viability (Georgia Closing Attorneys)

## 1. Niche Audit & Viability Scorecard

**Niche:** Real Estate Closing Attorneys and Title/Escrow Agents in Georgia
**Directory Family:** People (Licensed Attorneys, Law Firms)
**Target Audience:** Home buyers, sellers, real estate agents, lenders, and investors.

### Viability Filters (Rule R-116 & R-115)
* **Demand Concentration:** **HIGH.** The target audience is actively under contract to purchase or sell a property. This is a highly concentrated, transaction-ready buyer persona with immediate commercial intent.
* **Recurring Need (Scale vs. Frequency):** **MODERATE.** While a single retail home buyer may only need a closing attorney every 7-10 years (Low Frequency), the **Geographic Scale** encompasses all 159 Georgia counties. Furthermore, the B2B side (real estate agents, investors, wholesalers) has a High Frequency need (multiple deals per year).
* **Avatar Adjacency Cluster:** **STRONG.** The core avatar (real estate investor / home buyer) immediately needs adjacent services: Home Inspectors, Land Surveyors, Title Insurance, and Property Insurance. This offers a robust expansion path for future directory silos.

**Decision:** APPROVED for Stage 1 Deployment.

---

## 2. Programmatic Keyword Research (AnswerThePublic)

*Note: ATP queries are currently executing via `fetch-atp.py`. The preliminary search intent map is outlined below.*

**Core Terms Executed (9 Remaining Credits):**
1. `"investor friendly closing attorney"`
2. `"double closing attorney georgia"`
3. `"subject to closing attorney"`
4. `"clear title defect georgia"`
5. `"quiet title attorney"`
6. `"heir property lawyer georgia"`
7. `"who pays the closing attorney in georgia"`
8. `"georgia real estate transfer tax"`
9. `"commercial real estate closing attorney georgia"`

---

## 3. Search Intent Map & Geo-Multiplexing Plan

Based on the target persona and expected ATP keyword branches, we map the search intents to our programmatic generation plan:

### A. Implicit Localized Pages (General Educational Guides)
* **Search Intent:** "What does a closing attorney do in Georgia?" / "Who pays the closing attorney?"
* **Target URLs:** 
  * `/georgia-closing-attorney-requirements`
  * `/who-pays-closing-costs-georgia`

### B. Explicit Localized Pages (Geo-Multiplexed Hubs)
* **Search Intent:** "best closing attorney in [City]" / "[County] title agents"
* **Target URLs:**
  * `/[city]-real-estate-attorneys` (e.g., `/macon-real-estate-attorneys`)
  * `/[county]-closing-lawyers` (e.g., `/bibb-closing-lawyers`)

### C. Transactional Q&A (Listing Detail Level)
* **Search Intent:** "Does [Firm Name] handle wholesale double closings?" / "What are [Firm Name]'s escrow wire instructions?"
* **Mapping:** These intents are handled by the 7-question **Phase 1 LLM Enrichment** fields directly injected into the individual attorney profile pages (Layer 4 schema).

---

## 4. Value-First Reciprocity Utility
* **Tool:** Seller Net Sheet & Closing Cost Estimator
* **Logic:** Calculates estimated Georgia Transfer Tax ($1 per $1,000 of sales price), County Recording Fees, Title Search, and Attorney fee.
* **Placement:** Above the fold on all Discovery Hub and City Hub pages.
