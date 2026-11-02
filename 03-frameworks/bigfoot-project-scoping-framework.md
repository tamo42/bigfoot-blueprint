# Bigfoot Project Scoping Framework

How an AI agent runs a **new-project scoping conversation** in the Bigfoot Blueprint control plane: turning Neal's loose idea into an approved, phase-by-phase scope that a fresh agent session can pick up cold and run one step at a time. Use it when someone says "I want to build / fix / launch / automate X" and no project files exist for X yet.

This is one of three paired documents. **Scoping** (this file) produces the scope. The **Operation Framework** (`bigfoot-project-operation-framework.md`) says how one agent runs one step of it. The **Orchestrator** (`bigfoot-project-orchestrator/`) runs many steps in a row. Adapted from the Tax Sherpa OS `1065`, `1073` and `1074` frameworks; the logic flow is the same, the vocabulary is local (R-rules, BLEEP files, flat `p1_`-`p4_` file names, directory sites as sister repos).

Applies to a directory launch (a new niche), a change to an existing site, a pipeline or tooling project, or an SEO/analytics fix. It does not apply to work *inside* a scoped project (use that project's own PRD), or to one-off questions and small script tweaks. Scoping effort is proportional to the project.

---

## Naming and layout (used by all three documents)
A project has a **key**: the factory-phase prefix it mainly belongs to (R-126: `p1` selection, `p2` discovery, `p3` engineering, `p4` deployment/operations) plus a short slug, e.g. `p4_canonical`, `p3_az-wells`. Files are flat, in the owning niche's folder `02-workbench/<niche-folder>/` (R-113, R-126: no deep phase trees):

| File | Purpose |
| :-- | :-- |
| `<key>_prd.md` | Layer 1, the coordinating PRD |
| `<key>_phase-<N>-<slug>.md` | Layer 2, one per phase, created at scaffold time |
| `<key>_reference.md` | Facts, paths, commands and exact code a cold agent needs (a seed input to every phase) |
| `<key>_evidence/` | Phase outputs, readouts, baselines, findings |
| `<key>_runs/<date>/` | Orchestrator run logs and digests (only if the orchestrator is used) |

A cross-site project with no niche folder uses `02-workbench/_cross-site/`. Generalizable scripts go in `/scripts`, with a `scripts/README.md` entry (R-113, R-131); temporary work goes in `/scratch`. Project-level status lives in the PRD status line and one row of `01-context/project-index.md`. (`p4_canonical` predates this layout: its PRD is `p4_canonical_trailing_slash_plan.md`.)

---

## The Scoping Sequence
Run Pass 0 to Pass 6 in order. Passes 1-4 each map to a BLEEP file in the repo root: read it at the start of the pass so its rules are live, then apply it to *this* project rather than reciting it.

### 0. Value gate: is this worth scoping now?
One line each, sized to the idea:
- **Why now:** what makes it worth doing this month.
- **Displaces:** the active or queued project that slips.
- **For whom:** the person or avatar who uses the output (R-115 avatar).
- **Kill criterion:** the observable result at which the project is dropped.
- **Size:** S (one phase), M (2-3 phases), L (4+ phases, or a new site repo). L needs Neal's go-ahead before Pass 1, recorded in the PRD Decisions Log.

### 1. Intent: what does success look like? (`01_intent_manifest.bleep.md`)
- The objective in one sentence.
- What "done" concretely looks like: a metric, deliverable or behavior, checkable. Prefer the manifest's measures (indexing rate, schema validity, Lighthouse, reciprocity conversion).
- What is explicitly **out of scope** (an unbounded objective is the fastest way to bloat a scope).

### 2. Context boundary: what does it touch, and what must it leave alone? (`02_context_boundary.bleep.md`)
- Which niche folder and which site repo(s) under `C:\Users\tamo4\git\bigfoot-sites\` does it touch? Stage 1 (SQLite in Git, static Astro) or Stage 2 (multi-tenant Supabase)? Which factory phase (R-126)?
- Which data does it read or write? Directory data comes only from verified public registries (R-109: no fabricated regulatory fields). Raw scrapes go in `/cache/`.
- Non-functional check, one line each ("none" is valid); anything else becomes a Risk and, if it needs work, an acceptance criterion:
  - **Security:** credentials load from local `.env` only, never committed (02_context_boundary).
  - **Cost:** paid APIs and credits (geocoding R-101, ATP budget R-107, Apify/OpenAI/Places wallets R-111, Gemini calls).
  - **Accessibility:** the widget and standards of R-129; unclaimed listings never show negative badges (R-110).
  - **Rollback:** how a bad release is undone (git revert and redeploy; a Supabase migration needs its own down step).
- **Push boundary:** commit and push only in the named repo (GEMINI.md rule 5); never `neal-os`, `tax-sherpa` or `resilient-roots`. A push to a site repo **deploys to production** (Railway), so deploy steps are always flagged (Operation Framework §2).
- Running the project afterward is governed by the Operation Framework, not by this document.

### 3. Mechanism blueprint: how does it run, stage by stage? (`03_mechanism_blueprint.bleep.md`)
- Break the work into numbered stages with input, process and output artifact. For a new directory the stages are the blueprint states: Selection and Viability → Agentic Discovery → Engineering Pipeline → Antigravity Deployment (R-126).
- **Reuse check:** look in sibling `02-workbench/` projects, `/scripts`, and the other site repos before assuming something is new. Name what was checked.
- Scrape or enrichment steps follow R-106: small, self-contained, iterative, non-duplicate; verify on a small run before scaling.

**Phased implementation plan.** Anything with more than one discrete change decomposes into isolated phases:
- One phase = one deployable, reviewable, revertible change.
- Number phases by dependency, not by the order ideas came up: a flat sequence is `1, 2, 3`; phases that cluster under a category are `2.1, 2.2`. Draw the dependency graph first.
- Order by dependency-clearing. When two phases are equally free to go, pick one and state the tiebreak (de-risk the riskier one, unblock more work sooner, or lower rework cost), so a fresh agent does not re-litigate it.
- Record the phase list (number, description, dependency, isolation boundary). It becomes the PRD phase index and the seed of each phase doc.

**Decision closure.** Before the scope goes for approval, every open decision from Passes 1-3 is resolved (answer, who, when) or scheduled:
- Unresolved and another phase depends on it: a **decision phase** whose output is the recorded decision, listed in the index with each dependent's `Depends on` naming it.
- Unresolved and nothing depends on it: logged in its phase with a recommendation.
A scope with an unscheduled open decision is not ready for approval.

### 4. Feedback loop: how will it learn from corrections? (`04_feedback_loop.bleep.md`)
- Rules for this project go in the repo-root `.system-rules.md` as new `R-xxx` entries when they would apply beyond the project; a project may keep `<key>_rules.md` only for rules that apply to it alone.
- Name any correction class likely to recur (a scraper parse bug, enrichment prompt drift, a link or schema mistake). The abstraction threshold is fixed: corrected by hand 3-5 times → logged as a rule.

### 5. Scaffold and handoff: write the approved scope into the repo
Produce, in order:
1. A row in `01-context/project-index.md` (key, one-line purpose, status Draft, PRD path).
2. `<key>_prd.md` (Layer 1) and one `<key>_phase-<N>-<slug>.md` per phase (Layer 2), plus `<key>_reference.md`. Do not leave the scope only in the chat transcript.
3. **Zero-knowledge test.** Before approval, read each phase doc plus the Reference as if you had never seen the conversation. If you could not carry out the first step from those alone, add what is missing to the Reference. This is the scoping equivalent of the Operation Framework's cold-start test.

### 6. Two-layer PRD structure
Every project with **two or more phases** has both layers from scaffold time. A single-phase project uses the PRD alone; when a second phase appears, create the index table and a phase doc for every phase, including the first. The split is unconditional: "extract a phase once it gets big" is a judgment call made under time pressure, and it is how PRDs grow unbounded.

**Layer 1: `<key>_prd.md`** holds global scope and coordination only:
- Value gate, objectives, out-of-scope list, context boundary, mechanism and architecture.
- Cross-phase safety rails (constraints that apply project-wide).
- A **phase index table**: number, description, dependency, isolation boundary, status, approval, link. It is the only place "what phase are we on" is answered. **Approval** holds `Pending` or `Approved <date> (Neal)`, per phase; a phase never starts before its own row is approved, and approving one never approves another. Status values: Operation Framework §7.
- A Decisions Log limited to decisions that change the overall scope, reorder phases or affect more than one phase.
- Four required blocks: **Risks and assumptions** (effect if wrong, phase threatened); **Open questions** (each resolved, scheduled as a decision phase, or logged in its phase; or "none"); **Owners** (who approves scope and boundaries, who answers each decision); **Traceability table** (each objective → phases → the acceptance criterion that proves it; an objective with no phase, or a phase serving no objective, is a scoping defect).
- Never a phase's implementation steps, findings or verification detail.

**Layer 2: `<key>_phase-<N>-<slug>.md`**, shaped by Operation Framework §3:
- **Steps** are numbered `N.1, N.2, ...` with their dependencies.
- **Acceptance criteria** are fixed at scoping. Each names an invariant or a real-data check and the evidence that will show it met. A line that can only be judged by reading it says who looks. A phase with no checkable criterion is not ready for approval.
- **`Writes:`** names whole folders (or repos), never individual files, and includes every output folder the steps send output to. Name one file only to scope something narrower than a folder on purpose (for example one config file in a folder the phase does not own). Before approval, check every output path in the steps against `Writes:`; a path outside it is a scoping defect fixed now, not a question for Neal at run time.
- The doc declares itself self-contained, links back to the PRD, and lists its **seed inputs** (always the Reference).

### Re-scoping an approved scope
What counts as a re-scope is set in Operation Framework §7. A step agent that hits one stops and asks. Procedure, run by the agent Neal assigns:
1. **Draft, do not edit.** Write the revised scope as a draft in `<key>_evidence/`; the live PRD and phase docs stay as approved until step 4.
2. **Re-run the passes the change falsifies.** Whole-PRD tier: restart at the earliest pass whose answer changed (Pass 0 if the kill criterion or size moved, otherwise Pass 1) and carry through Pass 3, adding Pass 4 only if the correction classes changed. Affected-phases tier: re-run Pass 3 for the named phases and everything downstream; leave the rest alone.
3. **Re-derive dependent records:** index rows, acceptance criteria, traceability, any new decision phase.
4. **Neal re-approves.** Whole PRD: it is `Draft` until he does, every open phase is Blocked, every Approval cell is re-stamped. Affected phases: only those and their downstream phases return to `Pending`.
5. **Apply and clear the block.** Record the approval, rewrite each unblocked phase's Next-step block, and log the re-scope in each affected phase and, if more than one, as one PRD Decisions Log entry.

---

## Operating notes
- **It is a conversation, not a form.** Cover Passes 1-4 in whatever order flows, but confirm all four are covered before writing the scaffold; do not let "let's just start building" skip the boundary or feedback passes.
- **Minimal context loading.** Read `directory-registry.md`, the project index and the specific sibling projects named as reuse candidates, and stop there.
- **Nothing starts until Neal approves, phase by phase.** The PRD stays `Draft` until Neal approves the first phase; each Approval cell authorizes that phase alone. An agent never treats its own scoping output as authorization to build.
