# Phase 3: Internal links, script-built links and structured data (Project: uswelldrillers canonicalization)
**Status (2026-11-02):** Not started · Approval: Pending. Matches `p4_canonical_trailing_slash_plan.md` index. Depends on Phase 2 Complete.
**Writes:** site repo `C:\Users\tamo4\git\bigfoot-sites\uswelldrillers.com\src\components\`, `...\src\pages\`, `...\dist\` (build output); `...\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p4_canonical_evidence\`.
**Seed inputs:** `p4_canonical_reference.md` (§7 link inventory, §8 JSON-LD inventory, §10 live checks); `scripts/seo_canonical_audit.py`; Phase 2's `<date>-phase-2-local-audit.txt`.
Self-contained for a fresh session; coordinating PRD: `p4_canonical_trailing_slash_plan.md`.

## Why this phase exists
Even with canonical tags, internal links that point at non-slash URLs keep telling Google those are the real pages and send visitors through the wrong variant. Links built in browser JavaScript (search dropdown, calculator, county funnel) and the JSON-LD `url` fields must agree too.

## Steps
| Id | Title | Output | Depends on |
| :-- | :-- | :-- | :-- |
| 3.1 | Fix static template links | the files in Reference §7 "Static templates" edited so every internal href ends in `/` | none |
| 3.2 | Fix script-built links | the files in Reference §7 "Script-embedded links" edited (incl. `/search/?q=` and `/#` fragment forms like `.../-well-pump-troubleshooting/#...`) | none |
| 3.3 | Fix JSON-LD urls | the entries in Reference §8 edited | none |
| 3.4 | Local build and audit | `<date>-phase-3-local-audit.txt` showing all checks C1-C7 | 3.1, 3.2, 3.3 |
| 3.5 | Local click-through (human, Owner: Neal) | Neal's pass/fail from `npm run preview`: type in the home-page search box and click a result; run a calculator and click its guide link; use the county funnel button on `/pump-diagnostics/`; confirm each lands on a slash URL with no 404 | 3.4 |
| 3.6 | Commit and deploy (**Deploy**, Owner: Neal: the agent commits, Neal pushes) | one commit `fix(seo): trailing slashes on all internal links and schema urls` pushed to `master` | 3.5, phase Approved |
| 3.7 | Live verification | `<date>-phase-3-live.txt`: Reference §10 checks plus a live audit of the 20 sample pages' anchors | 3.6 |

## Acceptance criteria
1. Audit on the built site: C1-C7 all pass (every check clean, exit 0).
2. A repo search for the "Current" strings in Reference §7 and §8 finds none left (record the grep output).
3. Neal's click-through (3.5) passes with no 404 and no redirect.
4. Live: the 20 sample URLs return `200`, one correct canonical, and no on-site anchor in their HTML lacks a trailing slash (evidence in the live file).
5. Lighthouse performance on `/` and one contractor page is still >= 90; the Umami script is present.
6. Commit hash recorded for rollback (`git revert <hash>`).

## Next step
**Output:** step 3.1: the static-template link edits from Reference §7, a table row at a time, no other changes in those files.
**Inputs:** Reference §7; the listed files in the site repo (line numbers may have drifted; search for the "Current" text).
**Done when:** `npm run build` succeeds and `python scripts/seo_canonical_audit.py --dist <site>\dist --site https://uswelldrillers.com` shows C4 passing (C5 and C7 may still fail until steps 3.2 and 3.3).
**Depends on:** none.

## Log
(empty)
