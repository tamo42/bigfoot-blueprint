# General Scripts Repository

This folder contains global, cross-project utility scripts and templates that are not tied to a specific Phase or workbench directory. 

As per System Rule **R-131**, every script is documented below.

---

### `check-domain.py`
* **What it does:** Domain availability checker that actively pings each domain (resolving IP via socket) and checks ICANN's RDAP endpoint.
* **Why it does it:** To programmatically check and discover available domains (like `.com` or `.net`) for new directory deployments.
* **Inputs:** Domain name strings (passed via CLI arguments).
* **Outputs:** Availability status printed to the console (e.g., `TAKEN`, `AVAILABLE`, `RATE_LIMITED`).

### `export_sample.py`
* **What it does:** Database exporter that pulls a single `APPROVED` article from the local queue database and dumps it into a sample Markdown file with frontmatter.
* **Why it does it:** Allows for quick, manual inspection of the LLM-generated article's format and quality without having to push it fully to an Astro directory repository.
* **Inputs:** Local SQLite database (`cache/content_queue.db`).
* **Outputs:** Markdown file saved locally at `cache/sample_post.md`.

### `newsjacking_engine.py`
* **What it does:** The core LLM content engine. It fetches Google News RSS feeds, extracts the raw HTML content using Trafilatura, and uses the Gemini API to rewrite the articles for niche directory blogs.
* **Why it does it:** To automatically generate high-quality, topical "thin-content armor" and blog posts for the directory sites to improve SEO.
* **Inputs:** Configuration from `source/niche_profiles.json` and live Google News RSS XML endpoints.
* **Outputs:** Rewritten, approved articles inserted into `cache/content_queue.db`.

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

### `scrape_powerbi_grid_template.py`
* **What it does:** A generic Playwright async script template used as a starter file for scraping virtualized, client-rendered PowerBI dashboards.
* **Why it does it:** Saved as a potential large resource template for multiple future Bigfoot projects, as many state regulatory agencies embed public registries inside PowerBI grids which defeat standard HTTP request scrapers.
* **Inputs:** A target `POWERBI_EMBED_URL`.
* **Outputs:** Extracted text arrays mapped into a programmatic dataset.

### `test_news_rss_pull.py`
* **What it does:** A localized testing sandbox to verify the RSS XML extraction and decoding logic.
* **Why it does it:** To safely test Python dependencies (like `trafilatura` and `googlenewsdecoder`) and specific Boolean search queries before committing them to the heavy, token-consuming `newsjacking_engine.py`.
* **Inputs:** Hardcoded niches and targeted Boolean Google News queries.
* **Outputs:** Console prints containing the parsed article titles, original links, and raw extracted text.
