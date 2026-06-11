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
      - CREDENTIAL SECURITY: API keys, Supabase connection strings, and service roles must be loaded exclusively from local `.env` files; never commit credentials to GitHub.
    </DATA_PROFILE_CONSTRAINTS>

    <WORKSPACE_MAPPING>
      - LAYER 0 (Identity): GEMINI.md (Workspace instructions and naming rules).
      - LAYER 1 (Frameworks): `CONTEXT.md` (task routing) and BLEEP Manifests (`01_intent_manifest.bleep.md` through `04_feedback_loop.bleep.md`).
      - LAYER 2 (Core Specs): `/source/bigfoot-blueprint-framework.md` (moats, stack, and SEO hierarchy).
      - LAYER 3 (References): `/references/` (workshop analyses, SWOT, setups, slides, and copywriting guides).
      - LAYER 4 (Scripts & Data): `/scripts/` (scraping, geocoding, and enrichment engines) and `directory.sqlite`.
      - LAYER 5 (Behavioral Rules): `.system-rules.md` (learning and rule logs).
    </WORKSPACE_MAPPING>
  </TAB_3_INPUT_BOUNDARY>

  <TAB_4_SYSTEM_AUDITOR>
    <QUALITY_ASSURANCE_GYROSCOPE>
      - EXPRESS 5 ROUTING COMPLIANCE: If building dynamic API backends, all routing wildcards must use the parameter brackets syntax: `app.get("/storage/{*filePath}")` or `app.get("/{*wildcard}")`. Bare asterisk routes are banned.
      - PORT COMPLIANCE: Containers and API servers must be configured to bind and listen on port 8080 (`PORT=8080`) in production environments for health check compliance.
      - SCHEMA QUALITY: Every compiled Astro view must contain validated JSON-LD schema (FAQPage, ItemList, or LocalBusiness/LegalService) injected into the `<head>` tag.
      - VALUE-FIRST VISIBILITY: Listing pages and geography hubs must contain at least one un-gated, client-side calculator (e.g. S-Corp Savings, Closing Cost Net Sheet, Pumping Frequency) in the primary viewport (above the fold).
      - AVOID MONOLITHIC CMS: Traditional bloated page builders (WordPress, Webflow) or slow CRM-hosted landing pages must not be used for frontend deployment.
    </QUALITY_ASSURANCE_GYROSCOPE>
  </TAB_4_SYSTEM_AUDITOR>

</LEAP_INSTRUCTION_SET>
