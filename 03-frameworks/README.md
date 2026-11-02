# 03-frameworks

Reusable, site-agnostic frameworks and runbooks for the Bigfoot Blueprint control plane. Nothing here is specific to one directory or site.

| Document | Question it answers |
| :-- | :-- |
| [bigfoot-project-scoping-framework.md](bigfoot-project-scoping-framework.md) | How do we turn an idea into an approved scope of phases and steps? |
| [bigfoot-project-operation-framework.md](bigfoot-project-operation-framework.md) | How does one agent run one step of that scope, and stop? |
| [bigfoot-project-orchestrator/README.md](bigfoot-project-orchestrator/README.md) | How do we run many steps in a row with fresh agents? (SOP, plus `prompts/` for the orchestrator, step agent and verifier) |

Flow: **scope** (Scoping) → **do one step** (Operation) → **do many steps** (Orchestrator). Supporting pieces: `01-context/project-index.md` (one row per project) and `scripts/secret_scan.py` (the verifier's credential check).

Adapted from the Tax Sherpa OS frameworks `1065`, `1073` and the `1074` orchestrator project, with local vocabulary: R-rules in `.system-rules.md`, the four BLEEP files, flat `p1_`-`p4_` file names (R-126), and directory sites as sister repos whose pushes deploy to production.
