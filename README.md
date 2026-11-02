# nhq-bigfoot-blueprint

Development and prototyping workspace for the **Bigfoot Blueprint Niche Directories** framework.

This repository hosts:
* Public registry scraping scripts (`gabar-scraper.py`, etc.)
* Programmatic LLM enrichment pipelines (`gabar-enricher.py`, etc.)
* Raw scraped cache files and data exports
* The local SQLite prototype database files (`directory.sqlite`)

---

## Workspace Structure
* `GEMINI.md` / `CONTEXT.md` - workspace rules, folder map and task routing; `directory-registry.md` - live sites and KPI board.
* `01-context/` - global context docs (`project-index.md`, status snapshots).
* `02-workbench/` - per-niche project work (`p1_`-`p4_` files; project PRDs and phase docs).
* `03-frameworks/` - site-agnostic scoping, operation and orchestrator frameworks.
* `scripts/` - cross-project scripts (see `scripts/README.md`), including `secret_scan.py`.
* `gabar-scraper.py` - Georgia State Bar Real Property Law section scraper.
* `gabar-enricher.py` - Gemini-powered profile enrichment pipeline.
* `directory.sqlite` - Active SQLite database containing scraped and enriched profiles.
* `/cache/` - Cached raw HTML pages from state bar profiles to avoid redundant network requests.
