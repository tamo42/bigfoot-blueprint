# PRD: uswelldrillers.com Canonicalization & Trailing-Slash Consolidation (coordinating PRD)

**Status (2026-11-02):** Draft. Scope not yet approved by Neal. Size L (6 phases): needs Neal's go-ahead before Phase 1 (see Decisions Log D-1).
**Project:** a sub-project of `03-WELLS` (US Well Drillers), `02-workbench/03-wells-water-well-drillers/`. No new project code is allocated.
**Layout:** this file is Layer 1 (coordinating). Layer 2 phase docs sit beside it: `p4_canonical_phase-<N>-<slug>.md`. Shared facts, exact code and command lists: `p4_canonical_reference.md` (the **Reference**). Every phase doc lists the Reference as a seed input. Files are flat and `p4_`-prefixed per R-126.
**Method:** `03-frameworks/bigfoot-project-scoping-framework.md` (how this scope was built), `03-frameworks/bigfoot-project-operation-framework.md` (how one agent runs one step; **authoritative for the loop, outcomes and status values**) and `03-frameworks/bigfoot-project-orchestrator/` (optional: runs many steps in a row). Project key: `p4_canonical`. This PRD predates the framework's file naming: the framework calls it `<key>_prd.md`; here it is `p4_canonical_trailing_slash_plan.md`, and the orchestrator is given this path.

---

## 1. Value gate (Pass 0)
- **Why now:** Google lists 6,066 pages as "Duplicate without user-selected canonical" and the number is rising. Only 6,359 of 19,600 known pages are indexed while clicks are growing every month (15 → 511, Jun to Oct 2026), so indexing is the limit on growth.
- **Displaces:** the roll-out of the same fix to other sites, and the "Discovered, not indexed" thin-content project. Both wait until this fix is proven.
- **For whom:** Neal (site owner), and homeowners searching for well drillers, who reach the pages Google chooses to show.
- **Kill criterion:** drop and revert if, after the Phase 3 deploy, weekly clicks fall more than 20% below the trailing 4-week average for 2 consecutive weeks (see Risks R-1). Stop and re-scope if Phase 6's 6-week check shows no decline in the duplicate count.
- **Size:** L.

## 2. Intent (Pass 1, `01_intent_manifest.bleep.md`)
**Objective:** every page of uswelldrillers.com is reachable at exactly one URL, `https://uswelldrillers.com/<path>/`, with every signal (canonical tag, internal links, structured data, sitemap, server redirects) agreeing, so Google consolidates its duplicate pages and indexes the intended ones.

**Done looks like:**
- A freshly built site passes `scripts/seo_canonical_audit.py` with all seven checks clean.
- The live site serves the same, verified by sampling.
- Search Console's "Duplicate without user-selected canonical" count declines over the 6 weeks after deploy, and sampled URLs show user-declared canonical = Google-selected canonical.

**Out of scope:** new content or pruning thin pages; other sites (georgiagreasetrap.com, gaclosinglawyers.com, etc.); the "Discovered, not indexed" project; adding meta descriptions; changing sitemap contents (it is already correct); Lighthouse improvements beyond not regressing; the `/claim/` page (link already removed 2026-11-02, uncommitted).

## 3. Context boundary (Pass 2, `02_context_boundary.bleep.md`)
- **Touches:** site repo `C:\Users\tamo4\git\bigfoot-sites\uswelldrillers.com` (code, deploy via GitHub to Railway); this repo (`scripts/`, this folder, root `.system-rules.md`); Google Search Console (Neal only); the domain's DNS and Railway domain settings (Neal only, Phases 4-5).
- **Does not touch:** `01-contexts/clients`-style PII (none exists here), other site repos, `neal-os`, `tax-sherpa`, `resilient-roots`. Push boundary: GEMINI.md rule 5.
- **Reads:** the site's SQLite file only through the existing build; no schema or data changes.
- **Non-functional:** **Security:** none (no credentials; DNS changes made by Neal). **Cost:** none expected; Phase 4 may recommend a free tier of a CDN/proxy, any recurring spend is a decision for Neal. **Accessibility:** none (canonical tags are invisible; link targets are unchanged). **Rollback:** git revert plus redeploy for code; restore the previous DNS or host setting for Phase 5 (Reference §11).
- **Location:** the work is in a sister repo (deployed site); the specs, scripts and plan live here, as the existing wells project does.
- **Stack constraints (02_context_boundary):** static Astro on Railway stays; no monolithic CMS; if Phase 5 chooses a custom server it must obey R-104 and R-105.

## 4. Mechanism (Pass 3, `03_mechanism_blueprint.bleep.md`)
Stages: audit and baseline → fix signals in code → fix at the server → ask Google to re-evaluate and watch. This is blueprint state `STATE_04_ANTIGRAVITY_DEPLOYMENT` work on an already-live site.
**Reuse check:** no existing canonical or audit tooling in this repo (`scripts/` has `check-domain.py` and news scripts only). `@astrojs/sitemap` already emits a correct sitemap. Nothing to reuse beyond that.
**Dependency graph:** `1 → 2 → 3 → 6`; `3 → 5`; `4 → 5`. Phase 4 (a decision phase) depends on nothing and can run any time before 5.
**Tiebreaks:** 2 before 3: the canonical tag is the strongest single signal and the smallest, lowest-risk change; shipping it alone also lets us see its effect separately. 4 may start while 2-3 are in progress (it only needs read-only DNS lookups and docs), but sequence it after 3 by default so one agent holds one change at a time; it must finish before 5. Phases 2 and 3 both write the site's `dist/`, so they never run in parallel.

### Phase index
| # | Phase | Depends on | Isolation boundary | Status | Approval | Doc |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | Baseline and audit tool | none | New script in this repo; read-only build of the site. No site code changes | Not started | Pending | `p4_canonical_phase-1-baseline-audit.md` |
| 2 | Canonical tag and trailing-slash config | 1 | Site: `astro.config.mjs`, `src/layouts/Layout.astro`. One deploy | Not started | Pending | `p4_canonical_phase-2-canonical-tag.md` |
| 3 | Internal links, script links, structured data | 2 | Site: `src/components/`, `src/pages/`. One deploy | Not started | Pending | `p4_canonical_phase-3-internal-links.md` |
| 4 | Decision: DNS provider and redirect mechanism | none | Read-only research; output is a recorded decision | Not started | Pending | `p4_canonical_phase-4-decision-redirects.md` |
| 5 | Server-level redirects | 3, 4 | External: DNS/host settings per the decision | Not started | Pending | `p4_canonical_phase-5-redirects.md` |
| 6 | Search Console resubmission and 6-week monitoring | 3 | Human actions in GSC plus dated checkpoint records | Not started | Pending | `p4_canonical_phase-6-gsc-monitoring.md` |
Statuses: Not started, In progress, Blocked, Awaiting approval, Complete, Cancelled. Approval holds `Pending` or `Approved <date> (Neal)`; a phase does not start until its own row is approved, and approving one phase never approves another. Phase 5 is Cancelled by Neal if the Phase 4 decision is "no redirects".

## 5. Feedback loop (Pass 4, `04_feedback_loop.bleep.md`)
- The repo-root `.system-rules.md` is the rule registry; this project has no local one. Phase 1 step 1.4 adds rule **R-132** (every directory site ships a canonical tag, one trailing-slash policy and apex/www consistency, and passes `seo_canonical_audit.py` before launch and after any template change).
- Correction class likely to repeat: a new template or script adds a link without a trailing slash. Guard: the audit's C4/C5 checks. If the same slash correction is made by hand 3-5 times after this project, abstract it into the rule per `04_feedback_loop`.

## 6. Objectives → phases → proof (traceability)
| Objective | Phase(s) | Acceptance criterion that proves it |
| :-- | :-- | :-- |
| O-1 Every page declares its one canonical URL | 2 | Phase 2 criteria 1-3 (audit C1, C2, C3 clean; live sample) |
| O-2 Links and structured data agree with the canonical | 3 | Phase 3 criteria 1-3 (audit C4-C7 clean; live sample) |
| O-3 The server serves one URL per page | 4, 5 | Phase 5 criteria (redirect matrix) |
| O-4 Google consolidates the duplicates | 6 | Phase 6 criteria (submission done; URL Inspection sample; duplicate count tracked) |
| O-5 The fix cannot silently regress | 1 | Phase 1 criteria (audit tested on seeded defects; rule R-132 logged) |

## 7. Risks and assumptions
| ID | Risk or assumption | Effect if wrong | Phase |
| :-- | :-- | :-- | :-- |
| R-1 | Some of today's top-ranking URLs are non-slash or www variants. Switching the preferred URL may cause a temporary dip while Google re-picks | Clicks drop for a few weeks; kill criterion in §1 | 2, 3 |
| R-2 | `trailingSlash: 'always'` keeps `/search-index.json` working (UNVERIFIED) | Site search breaks | 2 |
| R-3 | Railway static hosting may not support redirects (UNVERIFIED) | Phase 5 needs a proxy or custom server, or is cancelled | 4, 5 |
| R-4 | DNS provider unknown (Namecheap or GoHighLevel, per Neal) | Phase 5 blocked until Neal supplies access or the answer | 4 |
| R-5 | Canonical tags are hints; Google may still choose another URL | Duplicate count falls more slowly than hoped | 6 |
| R-6 | The audit cannot execute browser JavaScript; script-embedded links are caught by pattern scan (C5), so a link built differently could slip through | A non-slash link survives | 3 |
| A-1 | The stale-looking local `dist/` may not match what is live | Baseline numbers differ from the table in the Reference | 1 |
| A-2 | All data and templates needed are in the site repo; no DB changes | None expected | all |

## 8. Open questions
| ID | Question | Status |
| :-- | :-- | :-- |
| Q-1 | Where is DNS hosted and what redirect mechanism will be used? | Scheduled as decision phase 4; Phase 5 depends on it |
| Q-2 | Are the Phase 6 trend thresholds right? Proposal: duplicate count below 3,000 (half of 6,066) six weeks after the Phase 3 deploy; "not met" triggers re-scope, not failure of the phase | Not gated; logged in Phase 6 with this recommendation |
| Q-3 | Go-ahead for a size-L project | Open: Decisions Log D-1; nothing starts until Neal approves Phase 1 |

## 9. Owners
- **Scope and every phase boundary:** Neal (approval column).
- **Answers Q-1 and Q-2:** Neal. **DNS, Railway and Search Console actions:** Neal (agents have no access).
- **Phase work (code, scripts, records):** any agent holding the phase marker.

## 10. Decisions Log (project-wide decisions only)
| ID | Date | Decision | By |
| :-- | :-- | :-- | :-- |
| D-1 | 2026-11-02 | Size L go-ahead | **Pending** Neal |
| D-2 | 2026-11-02 | URL policy: trailing slash on all pages, apex domain, https (Reference §3) | Neal |
| D-3 | 2026-11-02 | The `/claim/<slug>` banner link on contractor pages (no target page exists) is removed. Done in the working tree of `src/pages/contractors/[slug].astro`, uncommitted. Committed on its own in Phase 2 step 2.5 | Neal |
| D-4 | 2026-11-02 | DNS provider recorded as unknown, "probably Namecheap or GHL"; to be settled in phase 4 | Neal |

---

## How to run this project
Follow `03-frameworks/bigfoot-project-operation-framework.md` (one step per session) and `01-context/project-index.md` (project row). Project-specific rules:
- Every phase's seed inputs include `p4_canonical_reference.md`. Evidence goes in `p4_canonical_evidence/`; orchestrator runs write to `p4_canonical_runs/<date>/` (add that folder to a phase's `Writes:` before using the orchestrator).
- **Deploy steps** (flagged `Deploy`, `Owner: Neal` in the phase docs: Phase 2 step 2.5, Phase 3 step 3.6, Phase 5 steps 5.2-5.3) change production. Pushing the site repo deploys it. Agents do not push the site repo; Neal does, or says "push approved" in chat for the specific step. The orchestrator stops at them (S15).
- Steps marked `(human)` or `Owner: Neal` (Phase 2 step 2.7, Phase 3 step 3.5, Phase 4 step 4.5, Phase 6 step 6.2) are done by Neal; agents report and stop.
- Commits: inside the one repo a step names; R-114 applies. Never touch `neal-os`, `tax-sherpa` or `resilient-roots`.

**Kickoff prompt (one step):** "Continue the project whose PRD is `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p4_canonical_trailing_slash_plan.md` under `03-frameworks/bigfoot-project-operation-framework.md`. Run its section 1 loop for one step, then stop." (The full kickoff text is in section 8 of that framework.)
