# Bigfoot Blueprint — Workspace Context & Control Plane

This workspace is the central control plane and prototyping repository for the **Bigfoot Blueprint Niche Directory Framework**. It maps the strategic operational architecture, data processing scripts, analysis documents, and active directory sites.

---

## 🗺️ Task Routing Table

| Task Type | Go To | Description / Reference |
| :--- | :--- | :--- |
| **Manage Agent Rules & Blueprints** | `/` (root) | Core BLEEP manifests (`01_intent_manifest.bleep.md` through `04_feedback_loop.bleep.md`). |
| **Niche Discovery & Keyword Audits** | [Perry's Directory Ideas.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/references/Perry's%20Directory%20Ideas.md) | Compilation of niche candidate opportunities, Belcher's lists, and keyword resources. |
| **Execute Scrapers & Data Extraction** | `/scripts/` | Scrapers (e.g. `gabar-scraper.py`) and raw files in `/cache/`. |
| **Run Programmatic LLM Enrichment** | `/scripts/` | Enrichment scripts (`gabar-enricher.py`) leveraging Gemini 2.5 Flash/Pro. |
| **Implement Astro + SQLite Frontends** | [bigfoot-blueprint-framework.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/source/bigfoot-blueprint-framework.md) | Specifications for flat URL semantic silos, Zillow-level listing feeds, and JSON-LD schema layouts. |
| **Deploy & Onboard Vibe-Coded Sites** | [Setup Guide - BanjoSoft.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/references/Bigfoot%20BluePrint%20Setup%20Guide%20to%20Vibe%20Coded%20Directories%20BanjoSoft.md) | Onboarding guide, environment setup, and deployment tutorials. |
| **Optimize Copy & Claiming Conversions** | [Persuasion.docx.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/references/Persuasion.docx.md) | Hormozi's Value-First Reciprocity Playbook and Cialdini's 7 Principles of Persuasion. |
| **Examine Asset Templates & Schemas** | [Julius' Directory Asset Pack.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/references/Julius'%20Directory%20Asset%20Pack.md) | Canonical layout code, schema formats, and outreach copy templates. |
| **Review Workshop Transcripts** | `references/` | Raw Ignite Mastermind workshop transcripts (Parts 1-7) and [workshop analysis](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/bigfoot-blueprint-workshop-analysis.md). |
| **Verify Strategic SWOT & Viability** | [swot.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/nhq-bigfoot-blueprint-swot.md) & [objective-analysis.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/bigfoot-framework-objective-analysis.md) | SWOT matrix and analysis of data extraction bottlenecks, lag, and claims verification. |

---

## 🛠️ Shared Resources

| Resource / Tool | Location | Contains |
| :--- | :--- | :--- |
| **Workspace Index** | [GEMINI.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/GEMINI.md) | Repository rules, active directories registry, and folder maps. |
| **Intent Manifest (BLEEP 1)** | [01_intent_manifest.bleep.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/01_intent_manifest.bleep.md) | Vision & quantifiable success conditions. |
| **Context Boundary (BLEEP 2)** | [02_context_boundary.bleep.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/02_context_boundary.bleep.md) | Tech stack boundaries & quality auditor gyroscopes. |
| **Mechanism Blueprint (BLEEP 3)** | [03_mechanism_blueprint.bleep.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/03_mechanism_blueprint.bleep.md) | 4-Phase build state machine. |
| **Feedback Loop (BLEEP 4)** | [04_feedback_loop.bleep.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/04_feedback_loop.bleep.md) | Learning rules & error adaptation. |
| **Active Rules Registry** | [.system-rules.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/.system-rules.md) | System-level rule abstractions compiled over runs. |

---

## 🧠 Core Architecture Axioms

Every directory launched under this framework must adhere to these three core operational rules:

1.  **Value-First Reciprocity:** Listing pages and county/city hubs must feature an un-gated, interactive tool or calculator (such as the *Seller Net Sheet* or *S-Corp Savings Calculator*) to solve immediate user pain and trigger the reciprocity conversion loop before presenting lead or claiming gates.
2.  **Zero-Cost Stage 1 Bootstrapping:**
    *   **Hosting:** Deploy 100% static HTML via Astro to Vercel/Netlify for $0/mo hosting costs.
    *   **Database:** Package the dataset in a local SQLite file committed directly to the code repository ($0/mo database cost).
    *   **Enrichment:** Run full 20-question profile enrichment programmatically using your **Google AI Ultra subscription (Gemini 2.5 Flash / Pro)** natively inside the Antigravity IDE, keeping LLM API billing at $0.
3.  **Multi-Tenant Stage 2 Consolidation:** When a site meets validation triggers (traffic glimmers or claimed listings), migrate it to a consolidated **Multi-Tenant Supabase Instance** partitioned by a `directory_id` column. This allows you to host up to 10+ validated Stage 2 directories on a single $25/mo Supabase Pro plan.
