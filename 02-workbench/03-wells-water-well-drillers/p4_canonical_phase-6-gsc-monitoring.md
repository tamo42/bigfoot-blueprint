# Phase 6: Search Console resubmission and 6-week monitoring (Project: uswelldrillers canonicalization)
**Status (2026-11-02):** Not started · Approval: Pending. Matches `p4_canonical_trailing_slash_plan.md` index. Depends on Phase 3 Complete (it does not wait for Phase 5; if Phase 5 completes during monitoring, note its date in the log).
**Writes:** `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p4_canonical_evidence\` only. The Search Console actions are done by Neal; agents cannot log in.
**Seed inputs:** `p4_canonical_reference.md` (§4 baseline numbers, §3 URL policy); `p4_canonical_evidence/gsc-2026-11-02/` (the baseline exports); the Phase 3 deploy date from `p4_canonical_phase-3-internal-links.md`'s log.
Self-contained for a fresh session; coordinating PRD: `p4_canonical_trailing_slash_plan.md`.

## Why this phase exists
Google only reconsiders pages when it recrawls them. Resubmitting the sitemap, asking for indexing of the key pages and clicking "Validate fix" speeds that up. Then results are checked against the baseline for 6 weeks, because canonical changes take weeks to show and can briefly lower clicks (Risk R-1).

## Steps
| Id | Title | Output | Depends on |
| :-- | :-- | :-- | :-- |
| 6.1 | Prepare the request list | `p4_canonical_evidence/gsc-actions.md`: 10 URLs (top 10 pages from `gsc-2026-11-02/` Performance `Pages.csv`, rewritten to `https://uswelldrillers.com/<path>/`) and click-by-click instructions for Neal: URL Inspection → Request indexing for each; Sitemaps → resubmit `sitemap-index.xml`; Indexing → Pages → "Duplicate without user-selected canonical" → Validate fix | none |
| 6.2 | Neal performs the actions (human, Owner: Neal) | Neal confirms done and the date; the agent logs it | 6.1 |
| 6.3 | Checkpoint at +1 week after the Phase 3 deploy | `<date>-gsc-week-1.md` | 6.2 |
| 6.4 | Checkpoint at +2 weeks | `<date>-gsc-week-2.md` | 6.3 |
| 6.5 | Checkpoint at +4 weeks | `<date>-gsc-week-4.md` | 6.4 |
| 6.6 | Checkpoint at +6 weeks and recommendation | `<date>-gsc-week-6.md` with a recommendation | 6.5 |
Each checkpoint: Neal exports the same GSC reports as the baseline (Page indexing "Why pages aren't indexed" table, Performance by month and by week, Sitemaps); the agent compares to the baseline and records: duplicate count, indexed count, not-indexed count, weekly clicks versus the trailing 4-week average, and URL Inspection results for the 10 URLs (user-declared canonical versus Google-selected canonical).

## Acceptance criteria
1. 6.2 confirmed by Neal with a date (all three actions: indexing requests, sitemap resubmitted, validation started).
2. Four dated checkpoints exist, each with the five numbers above and the comparison with the baseline (6,066 duplicates, 6,359 indexed, 13,240 not indexed).
3. At +6 weeks, for the 10 inspected URLs, Google-selected canonical equals the user-declared one for at least 8 (reported; fewer triggers a recommendation, not a failure).
4. Trend is reported, not pass/fail: the duplicate count at +6 weeks versus the proposed threshold of below 3,000 (Question Q-2; Neal may change it). If it did not fall, the recommendation says to re-scope.
5. Guard: if weekly clicks are more than 20% below the trailing 4-week average for 2 consecutive weeks at any checkpoint, end *decision needed* immediately with a recommendation to investigate or revert Phase 3 (kill criterion).

## Next step
**Output:** step 6.1: `p4_canonical_evidence/gsc-actions.md`.
**Inputs:** `p4_canonical_evidence/gsc-2026-11-02/` (unzip `Performance-on-Search` into a new empty scratch folder; read `Pages.csv`); Reference §3.
**Done when:** the file lists exactly 10 URLs, each with `https://uswelldrillers.com/` and a trailing slash, with no duplicate entries after normalizing www and slash variants, and the three instruction sections are present.
**Depends on:** none.

## Log
(empty)
