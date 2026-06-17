# Nationwide Water Well Contractors Progress Tracker

This document tracks the collection, extraction, and enrichment status of water well drillers and pump repair technicians across all 50 states for our nationwide directory.

---

## 📊 Summary Board

*   **Total States:** 50
*   **Completed:** 9 (Georgia, Michigan, Ohio, Pennsylvania, New York, North Carolina, Texas, Virginia, Arizona)
*   **Scraped & Cleaned:** 0
*   **In Progress:** 2 (Florida, Tennessee)
*   **Not Started:** 39
*   **Total Records Collected:** 4,515 (Unified Master Database)
*   **Enriched Records:** 4,347 (100% Phase 3 Complete)

---

## 📈 Volume Priority Rollout Plan

To maximize the nationwide directory's organic search value and consumer utility, we prioritize state data collection based on **estimated private water well counts (market demand)**:

### 🥇 Tier 1: Mega Volume (>1,000,000 Private Wells)
1.  **Michigan** (~1.8M wells) — **[Completed]**
2.  **Pennsylvania** (~1.5M wells) — **[Completed]**
3.  **New York** (~1.3M wells) — **[Completed]**
4.  **North Carolina** (~1.2M wells) — **[Completed]**
5.  **Ohio** (~1.1M wells) — **[Completed]**
6.  **Virginia** (~1.0M wells) — **[Completed]**

### 🥈 Tier 2: Data-Ready High Volume Targets (API/Bulk Found)
7.  **Florida** (654,475 wells) — **[In Progress]**
8.  **Maryland** (571,829 wells)
9.  **Montana** (313,780 wells)
10. **Missouri** (291,262 wells)
11. **Arizona** (232,366 wells)
12. **Oklahoma** (213,115 wells)

### 🥉 Tier 3: Pending / Manual Extraction (High Volume)
13. **California** (1,164,847 wells)
14. **Wisconsin** (839,398 wells)
15. **Texas** (730,236 wells) — **[Completed]**
16. **Minnesota** (565,657 wells)
17. **Indiana** (419,118 wells)
18. **Georgia** (15,637 wells) — **[Completed]**

---

## 📋 State-by-State Data Registries

| State | Status | Record Count | Est. Wells (Market Volume) | Data Source Type | Source URL / Agency | Technical Extraction Notes |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **Alabama** | Not Started | - | 40,493 | Search Portal Scraper | [ADEM AL-OpCert Search](https://opcert.adem.alabama.gov/) | Requires post-back scraper to query and extract active licensees by county/name. |
| **Alaska** | Not Started | - | 42,376 | State DNR List | [Alaska DNR Water Wells](dnr.alaska.gov/mlw/water/wrfact.cfm) | DNR provides water well logs and driller licensing registries. |
| **Arizona** | **Completed** | 168 | 232,366 | ADWR Registry | [ADWR Licensing](new.azwater.gov/permits-licensing) | Runbook & scripts in [scripts/arizona/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/arizona/). Automated scraper blocked by Cloudflare; list exported manually and processed. Database at [arizona_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/arizona_wells.sqlite). |
| **Arkansas** | Not Started | - | 91,190 | ADH Licensing | [ADH Well Contractors](healthy.arkansas.gov) | Arkansas Dept of Health publishes certified well drillers. |
| **California** | Not Started | - | 1,164,847 | DWR Registry | [California DWR Well Completion](water.ca.gov) | Handled by DWR. Regional district offices maintain license and well logs. |
| **Colorado** | Not Started | - | 604,915 | DWR Licensing | [Colorado Division of Water Resources](dwr.colorado.gov) | Roster of licensed well drillers and pump installers available. |
| **Connecticut** | Not Started | - | 329 | DCP License Lookup | [CT DCP License Verification](elicense.ct.gov) | Controlled by CT Department of Consumer Protection. |
| **Delaware** | Not Started | - | 166,954 | DNREC List | [Delaware DNREC Well Licensing](dnrec.delaware.gov) | DNREC Division of Water publishes licensed well contractors. |
| **Florida** | In Progress | - | 654,475 | WMD Fragmented | [Florida DEP WMD Portal](https://floridadep.gov) | Runbook in [scripts/florida/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/florida/). Details 5 regional Water Management District databases and extraction approaches. |
| **Georgia** | **Completed** | 354 | 15,637 | PDF Roster | [Georgia EPD Standards](https://epd.georgia.gov) | Runbook & scripts in [scripts/georgia/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/georgia/). Parsed 3 PDFs. Enriched with Places API (326 Place IDs). Database at [georgia_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/georgia_wells.sqlite). |
| **Hawaii** | Not Started | - | 5,307 | DLNR Commission | [Hawaii DLNR CWRM](dlnr.hawaii.gov/cwrm) | Commission on Water Resource Management lists licensed drillers. |
| **Idaho** | Not Started | - | 136,594 | IDWR Roster | [Idaho Dept of Water Resources](idwr.idaho.gov) | Offers a directory of licensed well drillers. |
| **Illinois** | Not Started | - | 307,028 | IDPH Registry | [IDPH Water Wells](dph.illinois.gov) | Illinois Dept of Public Health licensing roster. |
| **Indiana** | Not Started | - | 419,118 | DNR Water | [Indiana DNR Water Well Driller](in.gov/dnr/water) | Maintains online roster of licensed water well drillers and pump installers. |
| **Iowa** | Not Started | - | 423,264 | Iowa DNR | [Iowa DNR Certified Drillers](iowadnr.gov) | Certified well contractors list managed by DNR. |
| **Kansas** | Not Started | - | 355,331 | KDHE Licensing | [KDHE Water Well Program](kdhe.ks.gov) | Roster of licensed water well contractors. |
| **Kentucky** | Not Started | - | 103,271 | EEC Division of Water | [Kentucky Division of Water](eec.ky.gov) | Water well driller certification registry. |
| **Louisiana** | Not Started | - | 219,735 | DNR Office of Conservation | [Louisiana DNR Ground Water](dnr.louisiana.gov) | Licensing database for water well contractors. |
| **Maine** | Not Started | - | 78,593 | Maine Well Drillers Board | [Maine Well Drillers Commission](maine.gov) | Roster of licensed well drillers and pump installers. |
| **Maryland** | Not Started | - | 571,829 | MDE Board | [Maryland Board of Well Drillers](mde.maryland.gov) | MDE certifies well drillers, water conditioning installers. |
| **Massachusetts** | Not Started | - | 321,127 | MassDEP Roster | [MassDEP Well Driller Program](mass.gov/dep) | Roster of certified well drillers. |
| **Michigan** | **Completed** | 513 | ~1,800,000 | PowerBI Scraper | [EGLE Wellogic Roster](https://www.michigan.gov/egle/about/organization/drinking-water-and-environmental-health/water-well-construction) | Runbook & scripts in [scripts/michigan/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/michigan/). Playwright scraper extracted 666 records from virtualized PowerBI grid. Enriched with Places API (83 Place IDs). Database at [michigan_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/michigan_wells.sqlite). |
| **Minnesota** | Not Started | - | 565,657 | MDH Well Management | [Minnesota Dept of Health](health.state.mn.us) | Searchable directory of licensed well contractors. |
| **Mississippi** | Not Started | - | 160,405 | MDEQ Office of Land/Water | [MDEQ Water Well Driller](mdeq.ms.gov) | Maintains list of licensed water well drillers. |
| **Missouri** | Not Started | - | 291,262 | DNR Well Installation | [Missouri DNR Well Driller Registry](dnr.mo.gov) | Registry of permitted well and pump installation contractors. |
| **Montana** | Not Started | - | 313,780 | DNRC Board of Water Well | [Montana DNRC Well Drillers](dnrc.mt.gov) | Board maintains active list of licensed drillers. |
| **Nebraska** | Not Started | - | 257,239 | DHHS Licensure | [Nebraska DHHS Water Well Standard](dhhs.ne.gov) | Online lookup for certified water well contractors. |
| **Nevada** | Not Started | - | 136,177 | DWR Well Drilling | [Nevada Division of Water Resources](water.nv.gov) | Roster of licensed water well drillers. |
| **New Hampshire** | Not Started | - | 90 | NHDES Water Well Board | [NHDES Well Drillers](des.nh.gov) | Directory of licensed water well contractors. |
| **New Jersey** | Not Started | - | 106,443 | NJDEP Licensing | [NJDEP Water Supply](nj.gov/dep/watersupply) | Roster of licensed well drillers and pump installers. |
| **New Mexico** | Not Started | - | 259,206 | OSE Well Drillers | [NM Office of the State Engineer](ose.state.nm.us) | List of active, licensed water well drillers. |
| **New York** | **Completed** | 454 | 201,616 | DEC Registry | [NY DEC Water Well Drillers](https://appfactory.dec.ny.gov/WaterWell/Contractor_Search) | Runbook & scripts in [scripts/new-york/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/new-york/). Bypassed OutSystems API pagination using Playwright request interception. Enriched with Places API (383 Place IDs). Database at [new_york_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/new_york_wells.sqlite). |
| **North Carolina** | **Completed** | 813 | 6,061 | CSV Export | [NC DHHS Well Certification](https://www.dph.ncdhhs.gov/programs/environmental-health/north-carolina-well-contractors-certification/find-certified-well-contractor) | Runbook & scripts in [scripts/north-carolina/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/north-carolina/). Processed user-provided CSV export. Aggregated 813 companies from personnel list. Database at [north_carolina_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/north_carolina_wells.sqlite). |
| **North Dakota** | Not Started | - | 110,174 | ND Board of Well Drillers | [ND Board of Water Well Contractors](nd.gov) | Licensing roster. |
| **Ohio** | **Completed** | 497 | 890,071 | PDF Roster | [Ohio DNR Division of Water](https://water.ohiodnr.gov) | Runbook & scripts in [scripts/ohio/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/ohio/). Parsed 104-page PDF with header cleaning. Enriched with Places API (194 Place IDs). Database at [ohio_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/ohio_wells.sqlite). |
| **Oklahoma** | Not Started | - | 213,115 | OWRB Well Drillers | [Oklahoma Water Resources Board](owrb.ok.gov) | Roster of licensed well drillers and pump installers. |
| **Oregon** | Not Started | - | 396,830 | OWRD Licensing | [Oregon Water Resources Dept](oregon.gov/owrd) | Searchable directory of licensed well drillers. |
| **Pennsylvania** | **Completed** | 201 | 527,486 | HTML Parser | [PA DCNR Licensed Driller](https://www.iframeapps.dcnr.pa.gov/topogeo/LicensedDriller) | Runbook & scripts in [scripts/pennsylvania/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/pennsylvania/). Parsed 201 records from the server-rendered HTML table, including child grids. Enriched with Places API (179 Place IDs). Database at [pennsylvania_wells.sqlite](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/data/pennsylvania_wells.sqlite). |
| **Rhode Island** | Not Started | - | 22,649 | DEM Water Resources | [RI DEM Well Drilling](dem.ri.gov) | Maintains registered well drillers list. |
| **South Carolina** | Not Started | - | 23,449 | LLR Lookup Scraper | [SC LLR License Portal](https://verify.llronline.com) | Environmental Certification Board licensee database. Requires lookup scrape. |
| **South Dakota** | Not Started | - | 74,654 | DANR Roster | [SD DANR Water Well Drillers](danr.sd.gov) | Licensing roster of well drillers. |
| **Tennessee** | In Progress | - | 270,815 | Dataviewers Web Roster | [TDEC Report on Licensed Drillers](https://dataviewers.tdec.tn.gov) | Runbook & scripts in [scripts/tennessee/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/tennessee/). Oracle APEX portal. Diagnostic scraper created; headless request 403 Forbidden blocking detected. |
| **Texas** | **Completed** | 1,224 | 730,236 | State Open Data API | [Texas Open Data Portal (TDLR)](https://data.texas.gov) | Runbook & scripts in [scripts/texas/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/texas/). SODA API dataset 7358-krk7. Cleaned and unified. Fully enriched in master DB. |
| **Utah** | Not Started | - | 372,505 | Division of Water Rights | [Utah Division of Water Rights](waterrights.utah.gov) | Maintains list of licensed water well drillers. |
| **Vermont** | Not Started | - | 112,965 | DEC Water Well Advisory | [Vermont DEC Well Driller Program](dec.vermont.gov) | Roster of licensed well drillers. |
| **Virginia** | **Completed** | 472 | 64,488 | DPOR License Lookup | [Virginia DPOR Verification](dpor.virginia.gov) | Runbook & scripts in [scripts/virginia/](file:///c:/Users/tamo4/git/nhq-bigfoot-blueprint/02-workbench/03-wells-water-well-drillers/scripts/virginia/). Parsed records from DPOR contractor lists. Cleaned and unified. Fully enriched in master DB. |
| **Washington** | Not Started | - | 305,019 | Ecology Licensure | [Washington Ecology Well Drilling](ecology.wa.gov) | Roster of licensed well operators. |
| **West Virginia** | Not Started | - | 362 | DHHR Sanitarians | [WV DHHR Environmental Health](wvdhhr.org) | Certified water well drillers list. |
| **Wisconsin** | Not Started | - | 839,398 | DNR Well Drillers | [Wisconsin DNR Well Drillers](dnr.wisconsin.gov) | Online roster of registered well drillers and pump installers. |
| **Wyoming** | Not Started | - | 278,196 | SEO Licensure | [Wyoming State Engineer Office](seo.wyo.gov) | Roster of licensed water well drilling and pump installation contractors. |
