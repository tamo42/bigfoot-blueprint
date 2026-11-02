# Bigfoot Blueprint Control Plane

This workspace is the master control plane, registry, and playbook for the **Bigfoot Blueprint Niche Directories** framework. It coordinates development, data ingestion, enrichment, and tracking for all directory assets.

---

# Workspace Folder Map

```
nhq-bigfoot-blueprint/
├── GEMINI.md            (you are here)
├── CONTEXT.md           (start here for task routing)
├── README.md            (workspace overview)
├── 01_intent_manifest.bleep.md     (BLEEP Pillar 1: Vision & success criteria)
├── 02_context_boundary.bleep.md    (BLEEP Pillar 2: Systems bounds & security)
├── 03_mechanism_blueprint.bleep.md (BLEEP Pillar 3: Transaction state-machine)
├── 04_feedback_loop.bleep.md       (BLEEP Pillar 4: Closed-loop learning rules)
├── .system-rules.md     (Layer 5 rules registry)
├── directory-registry.md (Registry of active directory sites and status)
├── 01-context/          (Global context docs: project-index.md, status snapshots)
├── 02-workbench/        (Per-niche project work: p1_-p4_ files, project PRDs and phase docs)
├── 03-frameworks/       (Site-agnostic frameworks: scoping, operation, orchestrator)
├── source/              (Core blueprint specifications)
│   └── bigfoot-blueprint-framework.md
├── references/          (Workshop transcripts, slides, templates, and guides)
├── scripts/             (Cross-project scripts: scrapers, enrichment, secret_scan.py)
├── scratch/             (Temporary work; git-ignored)
└── cache/               (Raw cache files for scrapers)
```

---

# Routing Table

| Task | Go to | Read |
|---|---|---|
| Track active directory sites & domains | `/` (root) | [directory-registry.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/directory-registry.md) |
| Review the core architectural specifications | `/source` | [bigfoot-blueprint-framework.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/source/bigfoot-blueprint-framework.md) |
| Execute scrapers & data clean | `/scripts` | Relevant scraper scripts & `/cache/` |
| Execute programmatic Gemini enricher | `/scripts` | `gabar-enricher.py` or equivalent scripts |
| Look up workshop notes & transcripts | `/references` | Relevant transcript or analysis markdown files |
| Audit brand board, links & asset templates | `/references` | Julius' Asset Pack, Vital Links, Worksheet |
| Update AI rules and agent boundaries | `/` (root) | BLEEP manifests & [.system-rules.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/.system-rules.md) |
| Scope a new project (idea to phases and steps) | `/03-frameworks` | [bigfoot-project-scoping-framework.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/03-frameworks/bigfoot-project-scoping-framework.md) |
| Run one step of a scoped project | `/03-frameworks` | [bigfoot-project-operation-framework.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/03-frameworks/bigfoot-project-operation-framework.md) |
| Run many steps of a scoped project in a row | `/03-frameworks/bigfoot-project-orchestrator` | [README.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/03-frameworks/bigfoot-project-orchestrator/README.md) (SOP and prompts) |
| Find active projects and their status | `/01-context` | [project-index.md](file:///C:/Users/tamo4/git/nhq-bigfoot-blueprint/01-context/project-index.md) and the latest status snapshot |

---

# Source-of-Truth Rules

- **Framework & Control Plane Specifications:** `nhq-bigfoot-blueprint` is the definitive source of truth.
- **Scraped Data cache:** Cached locally in `/cache/` or committed to Google Drive archives.
- **Production Directory Data:** SQLite database committed to each site's Git repo (Stage 1) or Supabase multi-tenant instance (Stage 2).
- **Credentials & Environment Configs:** Stored in local `.env` files; never committed to version control.

---

# Global Operating Rules

1.  **Block Code Registry:** Bigfoot Blueprint is assigned prefix **`9001`** under the master OS block allocation.
2.  **Astro Design Principle:** Frontend directories must ship zero client-side JavaScript by default, unless using interactive client-side calculators.
3.  **Flat URL Constraint:** Avoid nesting URL slugs beyond 1-level depth (e.g. `site.com/listing-slug` and `site.com/compliance-slug`).
4.  **Reciprocity Prioritization:** Do not deploy any landing page or listings page without a functional, un-gated calculator or evaluation tool above the fold.
5.  **Push Boundary:** Whenever committing or pushing code within this workspace, target ONLY the `nhq-bigfoot-blueprint` repository or the specific directory site repository. Do not mix commands with `neal-os`, `tax-sherpa`, or `resilient-roots` repositories.
6.  **Phase-Prefixed File Organization:** Do not create deeply nested phase folders (e.g., `03-engineering/scripts`). Instead, enforce a flat prefixing system on workspace files (`p1_viability.md`, `p2_scraper.py`, `p3_enrich.py`, `p4_deploy.json`) to map directly to the 4-Phase Agent-Accelerated Factory Workflow.
7.  **Deploy Boundary:** A push to a directory site repo under `C:\Users\tamo4\git\bigfoot-sites\` deploys that site to production (Railway). Scoped-project agents and the orchestrator never push a site repo; Neal does, or approves the specific push in chat.
