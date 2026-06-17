# General Scripts Repository

This folder contains global, cross-project utility scripts and templates that are not tied to a specific Phase or workbench directory. 

As per System Rule **R-131**, every script is documented below.

---

### `check-domain.py`
* **What it does:** Domain availability checker that actively pings each domain (resolving IP via socket) and checks ICANN's RDAP endpoint.
* **Why it does it:** To programmatically check and discover available domains (like `.com` or `.net`) for new directory deployments.
* **Inputs:** Domain name strings (passed via CLI arguments).
* **Outputs:** Availability status printed to the console (e.g., `TAKEN`, `AVAILABLE`, `RATE_LIMITED`).

### `newsjacking_engine.py`
* **What it does:** The core LLM content engine. It fetches Google News RSS feeds, extracts the raw HTML content using Trafilatura, and uses the Gemini API to rewrite the articles for niche directory blogs.
* **Why it does it:** To automatically generate high-quality, topical "thin-content armor" and blog posts for the directory sites to improve SEO.
* **Inputs:** Configuration from `source/niche_profiles.json` and live Google News RSS XML endpoints.
* **Outputs:** Rewritten, approved articles inserted into `cache/content_queue.db`.

### `distribute_news.py`
* **What it does:** Distributes all approved newsjacking articles from the unified SQLite database (`cache/content_queue.db`) and saves them as Markdown files into the correct content directory for each active Astro site.
* **Why it does it:** To automate the final publishing step in the newsjacking pipeline, pushing generated content to their respective directory site repositories for static deployment.
* **Inputs:** Approved articles in `cache/content_queue.db`.
* **Outputs:** Markdown files with YAML frontmatter written to `gaclosinglawyers.com`, `georgiagreasetrap.com`, and `uswelldrillers.com` news content collections.

### `p3_crawl_websites.py`
* **What it does:** A multithreaded web scraper utilizing BeautifulSoup and requests that crawls a list of URLs to extract and save raw text.
* **Why it does it:** Required for Phase 3 LLM enrichment; it gathers the raw, on-page context of a business's website so that Gemini can process and structure the data.
* **Inputs:** List of URLs (usually parsed from a seed CSV).
* **Outputs:** Cleaned text files saved into a local cache directory.

### `p3_enrich_places_apify.py`
* **What it does:** A Google Places integration that programmatically triggers an Apify actor via the Apify API to fetch business reviews, ratings, and their website addresses.
* **Why it does it:** To flesh out programmatic directory profiles with authentic, third-party Google trust signals and missing contact data.
* **Inputs:** Seed listings (from CSV or KV store) and the `APIFY_API_TOKEN`.
* **Outputs:** Enriched JSON/CSV datasets returned from the Apify cloud.

### `p4_enrich_reviews_gemini.py`
* **What it does:** An advanced LLM batch enrichment script that fetches unrated directory contractors from an SQLite database, sends their raw Google Reviews text to the Gemini Flash 2.5 API for structured sentiment analysis, and assigns 1-10 "Driller Scores" across multiple dimensions.
* **Why it does it:** To programmatically transform raw, unstructured text reviews into actionable, numeric data points to populate directory scorecards and rank businesses.
* **Inputs:** Target SQLite database containing raw contractor reviews.
* **Outputs:** JSON-structured analysis payloads inserted directly back into the SQLite database.

### `scrape_powerbi_grid_template.py`
* **What it does:** A generic Playwright async script template used as a starter file for scraping virtualized, client-rendered PowerBI dashboards.
* **Why it does it:** Saved as a potential large resource template for multiple future Bigfoot projects, as many state regulatory agencies embed public registries inside PowerBI grids which defeat standard HTTP request scrapers.
* **Inputs:** A target `POWERBI_EMBED_URL`.
* **Outputs:** Extracted text arrays mapped into a programmatic dataset.

### `supervisor.py`
* **What it does:** A Python-based process watchdog that autonomously manages long-running scripts (like `p4_enrich_reviews_gemini.py`) in batched intervals. It captures real-time stdout streams, enforces strict process execution timeouts, and gracefully auto-kills and restarts child processes if they hang on network retry loops.
* **Why it does it:** To fully automate overnight/unattended pipeline execution by bypassing terminal security confirmations and silently healing transient network errors (e.g. Google SDK 503 errors).
* **Inputs:** A target Python script and batch limits.
* **Outputs:** Real-time terminal streams and automated process recovery.
