# Scripts Documentation

Automatically generated per Rule R-131 for scripts in `answerthepublic/scripts/`.

---

### `fetch-atp.py`
*   **What it does:** Fetches keyword suggestions and related search data from the AnswerThePublic API for specified queries, regions, and languages. It caches the raw API responses locally to prevent redundant API calls and generates human-readable Markdown reports summarizing the findings.
*   **Why it does it:** To automate and streamline the process of gathering comprehensive keyword research data from AnswerThePublic, providing local caching for efficiency and credit management, and producing structured, shareable reports for analysis.
*   **Inputs:**
    *   **Environment Variable:** `ANSWERTHEPUBLIC_API_KEY` (required, typically loaded from a `.env` file).
    *   **Command-line Arguments:**
        *   `--query` (required): One or more keywords or phrases to search for, separated by commas (e.g., `'well cost, well repair'`).
        *   `--region` (optional, default: `US`): The 2-letter ISO country code for the target region (e.g., `US`, `GB`, `DE`).
        *   `--lang` (optional, default: `EN`): The 2-letter ISO language code for the target language (e.g., `EN`, `ES`, `FR`).
    *   **User Interaction:** A "y/n" prompt in the console to confirm making new API calls if a configured credit governor limit is met during a batch run.
    *   **Files:** Existing `.env` file (for API key) and previously generated JSON cache files (to avoid re-fetching data).
*   **Outputs:**
    *   **Console Output:** Progress messages, API status updates, a summary of retrieved suggestions (total count, breakdown by source, top questions), and warning/error messages.
    *   **Files:**
        *   `cache/{normalized_query}_{region}_{lang}_raw.json`: A JSON file containing the raw, complete response from the AnswerThePublic API.
        *   `reports/{normalized_query}_{region}_{lang}_summary.md`: A Markdown-formatted report summarizing the keyword suggestions, grouped by category (e.g., Questions, Prepositions) and sorted by search volume, including columns for search volume and cost per click.
    *   **Directories:** Creates `cache/` and `reports/` directories in the parent directory of the script if they do not already exist.