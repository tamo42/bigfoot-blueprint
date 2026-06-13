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
* There is a strict limit of **10 or fewer** API searches per directory launch to conserve overall account credits.

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
