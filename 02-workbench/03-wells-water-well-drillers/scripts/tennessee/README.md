# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `scripts/scripts/`.

---

### `p2_scrape_tennessee.py`
* **What it does:** This script launches a headless Chromium browser, navigates to a specific Tennessee Department of Environment and Conservation (TDEC) data viewer URL, takes a screenshot of the page, and then performs a basic analysis of the page's interactive elements. It logs information about buttons and relevant links (e.g., those containing "download", "export" keywords) and checks if the page is an Oracle APEX application.
* **Why it does it:** This script serves as an initial reconnaissance tool for understanding the structure and potential data export capabilities of a specific TDEC web page. It helps to identify interactive elements, verify page load, and determine if the page uses a common framework like Oracle APEX, which can inform subsequent web scraping strategies.
* **Inputs:**
    * Hardcoded URL: `https://dataviewers.tdec.tn.gov/dataviewers/f?p=2005:39918`
    * The `p3_utils` module, expected to be located in `../general/p3_utils.py`, which provides helper functions like `resolve_path`.
* **Outputs:**
    * **Console output:** Displays status messages, the page title, details of the first 15 button elements (ID, class, text), details of links with relevant keywords (ID, text, href), and whether the page is identified as an Oracle APEX application.
    * **File:** A PNG screenshot of the visited page saved to `02-workbench/03-wells-water-well-drillers/tdec_screenshot.png`.