# Phase 5: Server-level redirects (Project: uswelldrillers canonicalization)
**Status (2026-11-02):** Not started · Approval: Pending. Matches `p4_canonical_trailing_slash_plan.md` index. Depends on Phase 3 Complete and Phase 4 Complete. Cancelled if Neal's Phase 4 decision is "no redirects".
**Writes:** `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p4_canonical_evidence\`. External systems named in Phase 4's recorded decision (DNS provider, Railway domain settings, and, only if that decision chose it, a CDN/proxy or a server added to the site repo). If the decision adds files to the site repo, Neal must widen this line (re-scope) before the step runs.
**Seed inputs:** `p4_canonical_reference.md` (§3 policy, §10 redirect matrix, §11 rollback); Phase 4's findings and decision (`p4_canonical_evidence/*-findings.md` and its log).
Self-contained for a fresh session; coordinating PRD: `p4_canonical_trailing_slash_plan.md`.

## Why this phase exists
Canonical tags are hints. Redirects are rules: `www.uswelldrillers.com/*` and non-slash URLs get a permanent (301) redirect to the one canonical URL, so the duplicate variants stop being crawlable at all.

## Steps
| Id | Title | Output | Depends on |
| :-- | :-- | :-- | :-- |
| 5.1 | Record the current settings | `<date>-phase-5-before.md`: the exact current DNS records and host/domain settings (screenshots or copied text from Neal), plus the redirect matrix run now (Reference §10) | none |
| 5.2 | Implement www to apex 301 (**Deploy**, Owner: Neal: DNS/host change) | the setting made as the Phase 4 decision specifies; written steps recorded in `<date>-phase-5-changes.md` | 5.1 |
| 5.3 | Implement non-slash to slash 301 (**Deploy**, Owner: Neal) | same, if the chosen mechanism supports it; otherwise record "not supported by mechanism" and rely on canonicals | 5.2 |
| 5.4 | Verify with the redirect matrix | `<date>-phase-5-after.md`: 5 URLs x 5 variants per Reference §10 | 5.3 |

## Acceptance criteria
1. Before-state is saved with enough detail to restore it.
2. Matrix: for each of 5 URLs, the apex https slash URL returns `200` and every other tested variant returns exactly one `301` whose `Location` is that URL; no chains, no loops, no `302`. (Non-slash rows may be "not supported" only if 5.3 recorded it.)
3. The 20 sample URLs from Phase 1 still return `200` with their canonical tags intact.
4. A rollback note names the exact setting to restore.
5. Static assets (`/favicon.svg`, `/search-index.json`, `/sitemap-index.xml`, `/robots.txt`) still return `200` with no redirect.

## Next step
**Output:** step 5.1: `p4_canonical_evidence/<date>-phase-5-before.md`.
**Inputs:** Phase 4's decision entry; Neal's copy of the current DNS and Railway domain settings; Reference §10 matrix commands.
**Done when:** the file lists the current records/settings and the matrix output, so the "before" state can be restored; Neal supplying the settings is a *blocked* outcome if not yet provided (`Unblock by: Neal pastes the current DNS records and Railway domain settings`).
**Depends on:** none.

## Log
(empty)
