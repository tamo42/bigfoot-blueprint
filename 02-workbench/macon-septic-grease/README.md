# Macon Septic & Grease Directory (`02-SEPTIC`)

This directory covers **Septic Pumping & Grease Haulers** operating in **Macon, GA (Bibb County)**. It acts as a static Stage 1 directory asset compiled via Astro and SQLite, optimized for SEO search queries and AI RAG (AEO) citations.

---

## 📋 Niche Overview & Local Regulations

To establish technical authority (AEO/SEO) and pass Google's Helpful Content filters, this directory hardcodes local regulatory codes and compliance parameters in the homepage, location pages, and listings views:

### Macon Water Authority (MWA) Grease Regulations
* **Inspections:** The MWA performs grease trap/interceptor inspections of commercial food service establishments on a **quarterly basis** (4 times/year).
* **The 25% Pumping Rule:** Interceptors must be pumped when the combined thickness of the Fats, Oils, and Grease (FOG) layer and Food Solids layer exceeds **25% of the liquid depth** of the tank, or at least **once per quarter**, whichever occurs first.
* **FOG Concentration Limit:** Discharge of wastewater with FOG concentrations exceeding **300 mg/L** is strictly prohibited.
* **Reporting Compliance:** Businesses must submit pumping manifests completed by an approved hauler to the MWA Grease Management Coordinator.

### Georgia Department of Public Health (DPH) Septic Regulations
* **Licensing:** Septic installation and septage hauling must be conducted by a state DPH-certified contractor.
* **County Permit:** In addition to state certification, pumpers must hold an active **County Septage Removal Permit** from the local health department.

---

## 🛠️ Operational Pipeline Checklist

The directory follows a standard 4-step pipeline:
1. **`scripts/fetch-seed.py`:** Programmatic crawl of Google Places Text Search to extract active local providers in Macon and Bibb County, outputting `septic-grease-seed.csv`.
2. **`scripts/import-seed.py`:** Bootstraps `data/directory.sqlite` and imports the CSV seed rows.
3. **`scripts/enrich-places.py`:** Enriches the database with precise details (coordinates, hours, and review snippets) via the Google Places Details API.
4. **`scripts/enrich-specialties.py`:** Scrapes provider homepages to extract service specialties.
5. **`scripts/enrich-profile-qa.py`:** Runs offline LLM enrichment (using Gemini 2.5) to write SEO-optimized profiles and 20 local compliance FAQs.
