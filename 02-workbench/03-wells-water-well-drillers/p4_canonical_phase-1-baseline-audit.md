# Phase 1: Baseline and audit tool (Project: uswelldrillers canonicalization)
**Status (2026-11-02):** Not started · Approval: Pending. Matches `p4_canonical_trailing_slash_plan.md` index.
**Writes:** `C:\Users\tamo4\git\nhq-bigfoot-blueprint\scripts\`; `...\02-workbench\03-wells-water-well-drillers\p4_canonical_evidence\`; `...\scratch\` (test fixtures); site repo `...\bigfoot-sites\uswelldrillers.com\dist\` (build output, git-ignored); and, on purpose as single files, `...\nhq-bigfoot-blueprint\.system-rules.md` (append R-132 only).
**Seed inputs:** `p4_canonical_reference.md` (§2 commands, §4 evidence, §9 audit spec, §10 sample set); `p4_canonical_trailing_slash_plan.md`.
Self-contained for a fresh session; other phases' detail is deliberately absent. Coordinating PRD: `p4_canonical_trailing_slash_plan.md`.

## Why this phase exists
Every later phase is proven by one tool, so the tool is built first and tested on seeded bad cases. The baseline records the "before" state (site numbers and Search Console exports) so later changes can be measured, not remembered.

## Steps
| Id | Title | Output | Depends on |
| :-- | :-- | :-- | :-- |
| 1.1 | Write the audit script and its README entry | `scripts/seo_canonical_audit.py` per Reference §9, and a section in `scripts/README.md` with the R-131 structure | none |
| 1.2 | Test the script on fixtures | two tiny fake `dist` folders in `scratch/` (one clean, one with one seeded defect per check C1-C7) and a log of the runs | 1.1 |
| 1.3 | Build the site and run the baseline audit | `p4_canonical_evidence/<date>-baseline-audit.txt` | 1.2 |
| 1.4 | Build the sample URL list and record live baseline | `p4_canonical_evidence/sample-urls.txt` (20 URLs, Reference §10) and `<date>-baseline-live.txt` (status and canonical result per URL, www and non-slash variants of 3 of them) | none |
| 1.5 | Archive the Search Console exports | files copied to `p4_canonical_evidence/gsc-2026-11-02/` | none |
| 1.6 | Add rule R-132 | R-132 appended to `.system-rules.md` | 1.3 |

## Acceptance criteria
1. Clean fixture: script exits 0. Seeded fixture: exits 1 and names each of the 7 checks with a count of at least 1 (evidence: the 1.2 log).
2. `scripts/README.md` has the five R-131 fields for the new script.
3. Baseline audit exists and states: total HTML pages (expected near 9,417, any number is acceptable if recorded), C1 failing on 100% of pages, C4/C5 reporting more than 0 non-slash links, C3 listing any difference from the live sitemap's 9,420 URLs.
4. `sample-urls.txt` has 20 lines; baseline-live shows `200` for slash, non-slash and www variants of 3 URLs (confirming the problem on the live site).
5. `gsc-2026-11-02/` contains the 3 PNGs and 2 zips named in Reference §4.
6. `grep -n "R-132" .system-rules.md` returns one line in the same style as R-131.

## Next step
**Output:** step 1.1: `scripts/seo_canonical_audit.py` and its `scripts/README.md` section.
**Inputs:** Reference §9 (spec) and §2; the R-131 text in `.system-rules.md`; the format of existing entries in `scripts/README.md`.
**Done when:** `python scripts/seo_canonical_audit.py --help` prints usage, and the script has all seven checks named C1-C7 in its output summary.
**Depends on:** none.

## Log
(empty)
