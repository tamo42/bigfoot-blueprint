# Bigfoot Directories Registry

This registry tracks the status, configuration, domains, and metrics of all niche directories launched under the Bigfoot Blueprint.

---

## 📋 Active Directory Sites (Live)

| Directory ID | Name | Target Niche | Region | Domain / URL | Git Repository | Hosting | Stage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01-GABAR** | Georgia Closing Lawyers | Real Estate Closing Attorneys | GA, USA | [gaclosinglawyers.com](https://gaclosinglawyers.com) | `tamo42/gaclosinglawyers.com` | Railway | **Stage 1** |
| **02-SEPTIC** | Georgia Grease Trap | Septic Pumping & Grease Haulers | GA, USA | [georgiagreasetrap.com](https://georgiagreasetrap.com) | `tamo42/georgiagreasetrap.com` | Railway (Auto Deploy) | **Stage 1** |
| **03-WELLS** | US Well Drillers | Water Well Drillers | USA | [uswelldrillers.com](https://uswelldrillers.com) | `tamo42/uswelldrillers.com` | Railway | **Stage 1** |

---

## 🚧 Projects in Development

Development follows the **4-Phase Agent-Accelerated Factory Workflow**:
- **Phase 1:** Viability
- **Phase 2:** Scraper / Data Collection
- **Phase 3:** Enrichment
- **Phase 4:** Deployment

| Directory ID | Name | Target Niche | Region | Current Phase | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **04-HVAC-HUB** | *TBD* | HVAC Commercial Hub | Atlanta, GA | **Phase 2 (Prototyping)** | Located in `02-workbench/04-hvac-hub-hvac-commercial-hub/` |
| **05-NOTARIES** | *TBD* | Mobile Notaries & Loan Signing Agents | TBD | **Phase 1 (Intent Mapping)** | Located in `02-workbench/05-notaries-mobile-notaries/`. Managed by Rodrigo. |

---

## 📈 Stage 1 Validation Metrics (KPI Board)

Directories listed below are in Stage 1 (Static SQLite + Astro) and are being tracked for promotion to Stage 2 (Dynamic Supabase).

*Upgrade Trigger: Indexing > 60%, Impressions > 500/wk, Clicks > 20/wk, OR Claims > 2 in 30 days.*

| Directory ID | Launch Date | Pages Generated | Indexing % (GSC) | Impressions/Wk | Clicks/Wk | Claims (30d) | Upgrade Eligible? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01-GABAR** | 6/14/26 | 5438 | 0.0% | 0 | 0 | 0 | **No** |
| **02-SEPTIC** | 6/13/26 | 714 | 0.0% | 0 | 0 | 0 | **No** |
| **03-WELLS** | 6/16/26 | TBD | 0.0% | 0 | 0 | 0 | **No** |

---

## 🔍 Future Niches to Investigate

| Target Niche | Region | Priority | Notes |
| :--- | :--- | :--- | :--- |
| Disaster Events | *TBD* | *TBD* | Uses data sources to populate disaster events as listings. Custom architecture (not typical zero-code version). |
| *TBD* | *TBD* | *TBD* | *Add ideas here...* |

---

## ❌ Rejected Niches

| Target Niche | Region | Reason for Rejection | Date Rejected |
| :--- | :--- | :--- | :--- |
| *TBD* | *TBD* | *Add reason here...* | *YYYY-MM-DD* |
