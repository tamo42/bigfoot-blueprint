# ICM CONTEXT BOUNDARY - BIGFOOT BLUEPRINT CONTROL PLANE

<LEAP_INSTRUCTION_SET>

  <META>
    <ID>bigfoot_context_boundary.bleep</ID>
    <PURPOSE>To define the sandbox environment, tech stack configurations, data profile constraints, and quality audits for the Bigfoot Blueprint workspace.</PURPOSE>
  </META>

  <TAB_3_INPUT_BOUNDARY>
    <TECH_STACK_SPECIFICATIONS>
      - Core Framework (Stage 1): Astro (static site generation, zero client-side JavaScript by default).
      - Core Framework (Stage 2): Astro (ISR/SSR hybrid) + Multi-Tenant Supabase (PostgreSQL).
      - Database (Stage 1): Local SQLite database (`directory.sqlite`) committed directly to Git.
      - Database (Stage 2): PostgreSQL database (Supabase) partitioned with a `directory_id` tenant column.
      - Enrichment Engine: Python script runners (`gabar-enricher.py`) utilizing Google AI Ultra native models within the Antigravity IDE.
      - Routing Server: Express 5 API Server (when hosting dynamically, adhering to `path-to-regexp` v8 wildcard bindings).
      - Hosting/Deployment: Vercel / Netlify Edge CDN.
    </TECH_STACK_SPECIFICATIONS>

    <DATA_PROFILE_CONSTRAINTS>
      - SOURCE OF TRUTH: `nhq-bigfoot-blueprint` is the master registry, configuration, and scripting control plane.
      - DATA RETENTION: Raw scraped cache (HTML/JSON) must be stored locally in `/cache/` or Google Drive references.
      - SEPARATION OF TENANTS: All verified directory entries in Supabase must carry a valid foreign key `directory_id` linking to the master site registry.
      - CREDENTIAL SECURITY: API keys, Supabase connection strings, and service roles must be loaded exclusively from local `.env` files; never commit credentials to GitHub. `/scripts/secret_scan.py` checks added lines and untracked files for credentials; the orchestrator's verifier runs it on every step.
      - SOURCE OF TRUTH: Framework and control plane specifications live in this repo. Scraped data cache lives in `/cache/` or Google Drive archives. Production directory data is the SQLite database in each site's Git repo (Stage 1) or the multi-tenant Supabase instance (Stage 2).
      - BLOCK CODE REGISTRY: Bigfoot Blueprint is assigned prefix `9001` under the master OS block allocation.
      - PUSH BOUNDARY: Commits and pushes target ONLY the `nhq-bigfoot-blueprint` repository or the specific directory site repository. Never mix commands with `neal-os`, `tax-sherpa`, or `resilient-roots`.
      - DEPLOY BOUNDARY: A push to a directory site repo under `C:\Users\tamo4\git\bigfoot-sites\` deploys that site to production (Railway). Scoped-project agents and the orchestrator never push a site repo; Neal does, or approves the specific push in chat.
    </DATA_PROFILE_CONSTRAINTS>

    <WORKSPACE_MAPPING>
      - LAYER 0 (Identity): `CLAUDE.md`, `GEMINI.md` and `README.md` are pointer files only. They route to the BLEEP manifests and `.system-rules.md`; no rules or specs live in them.
      - LAYER 1 (Frameworks): `CONTEXT.md` (task routing) and BLEEP Manifests (`01_intent_manifest.bleep.md` through `04_feedback_loop.bleep.md`).
      - LAYER 2 (Core Specs): `/source/bigfoot-blueprint-framework.md` (moats, stack, and SEO hierarchy).
      - LAYER 3 (References): `/references/` (workshop analyses, SWOT, setups, slides, and copywriting guides).
      - LAYER 4 (Scripts & Data): `/scripts/` (scraping, geocoding, and enrichment engines) and `directory.sqlite`.
      - LAYER 5 (Behavioral Rules): `.system-rules.md` (learning and rule logs).
      - LAYER 6 (Context): `/01-context/` (project index, status snapshots).
      - LAYER 7 (Projects): `/02-workbench/` (per-niche work; project PRDs, phase docs and evidence, flat `pN_` files).
      - LAYER 8 (Frameworks): `/03-frameworks/` (scoping, operation and orchestrator for scoped projects).
      - ROOT FILES: `directory-registry.md` (live sites, status, KPI board), `gabar-scraper.py` (Georgia State Bar Real Property Law scraper), `gabar-enricher.py` (Gemini profile enrichment), `directory.sqlite` (scraped and enriched profiles), `/cache/` (raw HTML pages from state bar profiles), `/scratch/` (temporary work; git-ignored).
    </WORKSPACE_MAPPING>

    <TASK_ROUTING>
      - Track active directory sites and domains: `directory-registry.md`.
      - Review core architectural specifications: `/source/bigfoot-blueprint-framework.md`.
      - Execute scrapers and data clean: `/scripts` plus `/cache/`.
      - Execute the programmatic Gemini enricher: `/scripts/gabar-enricher.py` or equivalent.
      - Look up workshop notes and transcripts, or audit brand board, links and asset templates: `/references`.
      - Update AI rules and agent boundaries: the BLEEP manifests and `.system-rules.md`.
      - Scope a new project (idea to phases and steps): `/03-frameworks/bigfoot-project-scoping-framework.md`.
      - Run one step of a scoped project: `/03-frameworks/bigfoot-project-operation-framework.md`.
      - Run many steps of a scoped project in a row: `/03-frameworks/bigfoot-project-orchestrator/README.md` (SOP and prompts).
      - Find active projects and their status: `/01-context/project-index.md` and the latest status snapshot.
    </TASK_ROUTING>
  </TAB_3_INPUT_BOUNDARY>

  <TAB_4_SYSTEM_AUDITOR>
    <QUALITY_ASSURANCE_GYROSCOPE>
      - EXPRESS 5 ROUTING COMPLIANCE: If building dynamic API backends, all routing wildcards must use the parameter brackets syntax: `app.get("/storage/{*filePath}")` or `app.get("/{*wildcard}")`. Bare asterisk routes are banned.
      - PORT COMPLIANCE: Containers and API servers must be configured to bind and listen on port 8080 (`PORT=8080`) in production environments for health check compliance.
      - SCHEMA QUALITY: Every compiled Astro view must contain validated JSON-LD schema (FAQPage, ItemList, or LocalBusiness/LegalService) injected into the `<head>` tag.
      - VALUE-FIRST VISIBILITY: Listing pages and geography hubs must contain at least one un-gated, client-side calculator (e.g. S-Corp Savings, Closing Cost Net Sheet, Pumping Frequency) in the primary viewport (above the fold).
      - ASTRO ZERO-JS: Frontend directories ship zero client-side JavaScript by default, except interactive client-side calculators.
      - FLAT URLS: Never nest URL slugs beyond 1-level depth (e.g. `site.com/listing-slug`, `site.com/compliance-slug`).
      - RECIPROCITY GATE: Do not deploy any landing page or listings page without a functional, un-gated calculator or evaluation tool above the fold.
      - AVOID MONOLITHIC CMS: Traditional bloated page builders (WordPress, Webflow) or slow CRM-hosted landing pages must not be used for frontend deployment.
    </QUALITY_ASSURANCE_GYROSCOPE>
  </TAB_4_SYSTEM_AUDITOR>

</LEAP_INSTRUCTION_SET>
