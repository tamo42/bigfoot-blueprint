# Phase 2 — Keyword Research & Search Intent Mapping

This document establishes the strategic keyword context for the **Water Well Drillers Directory**, mapping real-world homeowner queries (crawled via AnswerThePublic) directly to database design, crawler patterns, and value-first calculator specifications. 

Following the updated Bigfoot framework workflow, this research must be completed immediately after Niche Selection to shape all downstream technical assets.

---

## 1. AnswerThePublic Crawl Summary (Google Web US/EN)

We executed programmatic crawls across 9 highly variant root keywords. The resulting datasets are cached locally in `02-workbench/answerthepublic/cache/` and detailed in `02-workbench/answerthepublic/reports/`.

| Root Query | Total Suggestions | Primary Intent Category | High-Volume Search Example | Search Vol | CPC ($) |
| --- | --- | --- | --- | --- | --- |
| `well pump troubleshooting` | 75 | Alphabeticals (56) | *well pump troubleshooting pressure switch* | 390 | \$0.60 |
| `well drilling cost` | 280 | Alphabeticals (187) | *what is the cost of drilling a well* | 90 | \$7.76 |
| `well water testing` | 956 | Related (602) | *how much does well water testing cost* | 170 | \$3.52 |
| `well pump repair` | 357 | Related (233) | *how much is well pump repair* | N/A | N/A |
| `well pressure tank` | 1,354 | Related (822) | *how to install well pressure tank* | 590 | \$2.81 |
| `well water smell` | 244 | Alphabeticals (116) | *how to fix well water smell* | 90 | \$4.37 |
| `replace well pump` | 181 | Alphabeticals (123) | *how to replace well pump pressure switch* | 590 | \$1.81 |
| `water softener` | 2,834 | Related (2033) | *what water softener do* | 3,600 | \$3.40 |
| `solar well pump` | 244 | Alphabeticals (162) | *can you run a well pump on solar* | 10 | \$1.32 |

---

## 2. Intent-Driven Database Schema Configuration

To ensure our listings directory can filter and route users based on search queries, we map top keyword intents directly to boolean/text columns in the unified database (`water_well_directory.sqlite`):

1.  **Intent: High-Urgency Pump Diagnostics & Emergency Repairs**
    *   *High-Volume Queries:* *"who does 24/7 emergency well repair near me"* / *"well pump troubleshooting no water"*
    *   *Database Implementation:* Enforce column `has_24_7_emergency_service` (integer/boolean) in the main companies table.
2.  **Intent: Water Quality Testing & Health Compliance**
    *   *High-Volume Queries:* *"who does well water testing near me"* / *"how much does well water testing cost"*
    *   *Database Implementation:* Enforce column `has_water_testing_lab` or `offers_water_testing` (integer/boolean).
3.  **Intent: Capital Cost Projects & Bureaucracy Management**
    *   *High-Volume Queries:* *"cost of drilling a new well"* / *"who to call to drill a well"*
    *   *Database Implementation:* Enforce column `handles_new_permits` (integer/boolean) to track if the driller handles local DNR/county permitting.
4.  **Intent: Specific Equipment Maintenance**
    *   *High-Volume Queries:* *"well pressure tank replacement"* / *"replace well pump pressure switch"* / *"water softener installation"*
    *   *Database Implementation:* Enforce tag list or service flags `services_pressure_tanks`, `services_pressure_switches`, `installs_softeners`.

---

## 3. Scraper & Website Crawler Context

Rather than crawling websites for general keywords, the Phase 3 web crawler (`p3_crawl_websites.py`) will use targeted search lists matching the primary search intents:

*   **Pressure Switch & Tank Sourcing:** Instruct the LLM scraper to look for the terms `"pressure switch"`, `"bladder tank"`, `"well tank"`, `"rapid cycling"`, or `"pressure control"` on contractor sites to identify component-level diagnostic specialists.
*   **Water Smell Sourcing:** Look for terms like `"sulfur smell"`, `"rotten egg smell"`, `"iron staining"`, `"smelly water"`, `"aeration system"`, `"chlorination"` to identify water quality specialists.
*   **Drilling Capabilities:** Search for `"well drilling"`, `"air rotary"`, `"well casing"`, `"well rehabilitation"` to distinguish heavy drillers from light service technicians.

---

## 4. Reciprocity Calculator Sizing & Content Silos

The keyword data maps directly to the three tabs of our above-the-fold **Unified Well System Calculator** ([p2_reciprocity_calculator_spec.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/p2_reciprocity_calculator_spec.md)):

*   **Tab 1 (Sizing & Cost):** Directly addresses the questions *"what size well pressure tank do i need"* and *"cost of drilling a well per foot"* using physical equipment sizing calculations.
*   **Tab 2 (Diagnostics):** Addresses *"well pump troubleshooting pressure switch"* and *"what happens when well pressure tank goes bad"* using interactive guides.
*   **Tab 3 (Water Quality):** Addresses *"how to fix well water smell"* and *"what water softener do"* with treatment system matcher formulas.
