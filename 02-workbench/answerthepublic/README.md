# AnswerThePublic CLI Keyword Crawler

This directory hosts the shared keyword research utility outlined in **Rule R-107** to fetch and cache user search questions and queries from the AnswerThePublic API.

---

## Technical Specifications & Parameters

The CLI script (`scripts/fetch-atp.py`) interacts with the AnswerThePublic API to pull search questions (who, what, where, why, how, are, which, when) and comparisons.

### Command-Line Arguments
* `--query` (string, required): The target search term (e.g. `"grease trap"` or `"septic pumping"`).
* `--region` (string, optional): The target country region code (default: `"US"`).
* `--lang` (string, optional): The target language code (default: `"EN"`).

### Local Caching & Credit Conservation (Rule R-107)
* All successful API payloads are cached locally as JSON files inside `cache/<normalized-query>_raw.json`.
* Subsequent executions with the same query term will load data directly from the cache to prevent redundant credit billing on the API subscription.

### Strategic Workflow (The 10-Query Budget)
Due to strict API quotas and Rule R-107, keyword research must be executed in two phases (Max 10 searches per directory):
1. **Geographic Constraint:** Do NOT use local geographic modifiers in your `--query` (e.g., use `"grease trap"`, NOT `"Atlanta grease trap"`). ATP relies on broad autocomplete data and will return zero results for local tails. You must infer local volume from national broad intent.
2. **Phase 1 (Head Terms):** Run exactly 3 broad head terms to map the general landscape.
3. **Phase 2 (Avatar-Fitting):** Analyze the questions generated in Phase 1 to identify high-intent, avatar-specific modifiers. Use these discoveries to select your remaining 7 queries.

---

## Setup & Execution

### Environment Setup
Make sure the `.env` file in the root directory contains your API key:
```env
ANSWERTHEPUBLIC_API_KEY=your_atp_api_key_here
```

### Run Search Crawler
To execute a query:
```bash
python scripts/fetch-atp.py --query "grease trap" --region US --lang EN
```
This will fetch the questions, output a summary to stdout, and save the raw payload to the cache folder.
