# Phase 2: Canonical tag and trailing-slash config (Project: uswelldrillers canonicalization)
**Status (2026-11-02):** Not started · Approval: Pending. Matches `p4_canonical_trailing_slash_plan.md` index. Depends on Phase 1 Complete.
**Writes:** site repo `C:\Users\tamo4\git\bigfoot-sites\uswelldrillers.com\src\layouts\`; `...\dist\` (build output); `...\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p4_canonical_evidence\`; and, on purpose as a single file, the site repo's `astro.config.mjs`. Step 2.5 also commits the already-edited `src/pages/contractors/[slug].astro` (claim-link removal) without editing it again.
**Seed inputs:** `p4_canonical_reference.md` (§3 URL policy, §6 code, §10 live checks, §11 rollback); Phase 1's `scripts/seo_canonical_audit.py` and `p4_canonical_evidence/<date>-baseline-audit.txt`, `sample-urls.txt`.
Self-contained for a fresh session; coordinating PRD: `p4_canonical_trailing_slash_plan.md`.

## Why this phase exists
Google cannot tell which of `/x`, `/x/` and `www./x` to index because no page names its preferred URL. A canonical tag on every page is the strongest, smallest fix and ships alone so its effect can be seen separately. The trailing-slash setting makes Astro generate only slash URLs.

## Steps
| Id | Title | Output | Depends on |
| :-- | :-- | :-- | :-- |
| 2.1 | Set `trailingSlash: 'always'` and `build.format: 'directory'` | edited `astro.config.mjs` (Reference §6) | none |
| 2.2 | Add canonical and `og:url` to the layout | edited `src/layouts/Layout.astro` (Reference §6) | 2.1 |
| 2.3 | Local build and audit | `p4_canonical_evidence/<date>-phase-2-local-audit.txt` | 2.2 |
| 2.4 | Local preview check | `<date>-phase-2-preview.txt`: the sample URLs fetched from `npm run preview`, with status and canonical | 2.3 |
| 2.5 | Commit and deploy (**Deploy**, Owner: Neal: the agent commits, Neal pushes) | two commits in the site repo pushed to `master`: first `fix: remove dead /claim link` (only `src/pages/contractors/[slug].astro`), then `feat(seo): add canonical tags and enforce trailing slashes` | 2.4, phase Approved |
| 2.6 | Live verification | `<date>-phase-2-live.txt`: Reference §10 checks incl. Lighthouse for `/` and one contractor, and Umami script check | 2.5 |
| 2.7 | Rich Results look (human, Owner: Neal) | Neal's pass/fail on one page of each of 3 types in Google's Rich Results Test | 2.6 |

## Acceptance criteria
1. `npm run build` succeeds; the page count equals the Phase 1 baseline (state both numbers); `dist/search-index.json` exists and parses as a JSON array.
2. Audit on the new build: C1 and C2 pass (every page has exactly one canonical equal to its own https apex slash URL); C3 passes (canonicals equal the sitemap set). C4-C7 may still fail (Phase 3).
3. Live: all 20 sample URLs return `200` at the slash URL with one correct canonical; the earlier `/claim/` banner is gone from a contractor page.
4. Lighthouse performance >= 90 on `/` and one contractor page; the Umami script URL is still present.
5. Neal confirms the Rich Results Test is unchanged for 3 page types (or notes any regression).
6. Rollback tested on paper: the two commit hashes are recorded so each can be reverted.

## Next step
**Output:** step 2.1: `astro.config.mjs` with the two new keys, nothing else changed.
**Inputs:** `astro.config.mjs` in the site repo; Reference §6.
**Done when:** `npm run build` in the site repo succeeds and `dist/search-index.json` exists and `dist/` has the same number of `index.html` pages as the baseline; if `search-index.json` is missing, stop with *scope changed* (Reference §6, UNVERIFIED note).
**Depends on:** none.

## Log
(empty)
