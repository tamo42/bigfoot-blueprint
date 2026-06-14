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
├── source/              (Core blueprint specifications)
│   └── bigfoot-blueprint-framework.md
├── references/          (Workshop transcripts, slides, templates, and guides)
├── scripts/             (Scrapers and LLM enrichment pipelines)
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
