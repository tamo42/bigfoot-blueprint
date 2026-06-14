# Ohio Water Well Contractors Ingestion Runbook

This directory handles downloading, cleaning, and parsing active water well contractors for the State of Ohio.

---

## Data Source

*   **Agency:** Ohio Department of Health (ODH) / ODNR Division of Water
*   **Source Format:** PDF Roster
*   **Original URL:** [Ohio DNR Water Well Contractors Portal](https://water.ohiodnr.gov)
*   **WebSphere Listing Page:** `https://odh.ohio.gov/know-our-programs/private-water-systems-program/media/list-regpwsc-ohio`
*   **Target Download Path:** `cache/ohio_registered_pws_contractors.pdf`

---

## Technical Extraction Process & Quirks

The Ohio registry has two primary technical challenges:

1.  **WebSphere Dynamic Redirection:** Raw HTTP requests to `odh.ohio.gov` returns empty elements because components are rendered client-side via WebSphere JS portlets. Playwright is used in headless mode to navigate to the page, wait for the DOM to hydrate, and extract the generated PDF URL.
2.  **PDF Header Signature Pollution:** The downloaded PDF contains an injected HTML/JavaScript tag `<script>...</script>\r\n` preceding the PDF signature. This shifts the binary file signature by up to 192 bytes, which causes standard PDF readers like `pypdf` to crash with file format errors. The parser automatically scans the raw file bytes for `%PDF-`, programmatically strips the leading byte noise, and processes a cleaned temporary file.
3.  **Layout Columns Mapping:** The PDF is read in layout mode, and columns are extracted using hardcoded slice indices:
    *   `[0:45]` : License number and registration year.
    *   `[45:80]`: Company name and address lines.
    *   `[80:110]`: Owner/contact name, telephone, and date.
    *   `[110:]`: Service checkboxes.

---

## Execution Commands

Ensure you are at the workspace root (`nhq-bigfoot-blueprint/`) before executing:

```bash
# 1. Scrape the PDF link via Playwright
python 02-workbench/water-well-drillers/scripts/ohio/scrape_ohio.py

# 2. Extract layout text to a diagnostic sample file (for verification)
python 02-workbench/water-well-drillers/scripts/ohio/inspect_ohio_pdf.py

# 3. Parse PDF and initialize the SQLite database
python 02-workbench/water-well-drillers/scripts/ohio/parse_ohio_pdf.py

# 4. Enrich database listings using the general Places API enricher
python 02-workbench/water-well-drillers/scripts/general/enrich_places_general.py --state ohio --limit 100
```
