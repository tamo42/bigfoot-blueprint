# Phase 4: Decision: DNS provider and redirect mechanism (Project: uswelldrillers canonicalization)
**Status (2026-11-02):** Not started · Approval: Pending. Matches `p4_canonical_trailing_slash_plan.md` index. Decision phase: output is a recorded decision; Phase 5 depends on it.
**Writes:** `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p4_canonical_evidence\` only (read-only research otherwise).
**Seed inputs:** `p4_canonical_reference.md` (§3 URL policy, §10 redirect matrix, §12 unknowns 1-2); `p4_canonical_trailing_slash_plan.md` (Risks R-3, R-4).
Self-contained for a fresh session; coordinating PRD: `p4_canonical_trailing_slash_plan.md`.

## Why this phase exists
Google is told the preferred URL by canonical tags (Phases 2-3). Redirects make the server enforce it, so visitors and crawlers never see www or non-slash copies. How to build redirects depends on two unknown facts: where the domain's DNS is managed, and what Railway's static host can do. Neal must choose, so it is a decision phase.

## Steps
| Id | Title | Output | Depends on |
| :-- | :-- | :-- | :-- |
| 4.1 | Find the DNS provider | `p4_canonical_evidence/<date>-dns-findings.md`: output of `nslookup -type=NS uswelldrillers.com`, `nslookup -type=NS www.uswelldrillers.com`, `nslookup uswelldrillers.com`, `nslookup -type=CNAME www.uswelldrillers.com`, each with a plain reading (which provider the name servers belong to) | none |
| 4.2 | Find what Railway static hosting supports for redirects | `<date>-railway-redirect-findings.md`: Railway documentation read for redirect rules, www/apex handling, and custom domains on static services, each claim with its URL; unanswered questions marked unanswered | none |
| 4.3 | Find what the DNS provider supports | `<date>-dns-provider-redirect-findings.md`: the provider's documented redirect options (e.g. URL redirect records, proxy/CDN, rules) with sources | 4.1 |
| 4.4 | Options and recommendation | the decision entry in this log: 3-4 options (for example A: www-to-apex at DNS provider plus canonical tags only; B: CDN/proxy in front with redirect rules; C: small custom server; D: no redirects), cost, effort, risk, and a recommendation | 4.2, 4.3 |
| 4.5 | Neal's decision (Owner: Neal) | Neal's choice recorded in this log and as a `prd.md` Decisions Log row D-5 | 4.4 |

## Acceptance criteria
1. The DNS provider is named with command output as evidence, or marked unanswered with the reason.
2. Every claim about Railway and the DNS provider has a source URL; unknowns are marked unknown.
3. The options entry has at least options A, C and D, a cost for each (including "none"), and a recommendation.
4. Neal's choice is recorded with date; if "no redirects", Phase 5 is set to Cancelled by Neal.

## Next step
**Output:** step 4.1: `p4_canonical_evidence/<date>-dns-findings.md`.
**Inputs:** the four `nslookup` commands in step 4.1 run from this machine (PowerShell or Git Bash).
**Done when:** the file contains the raw command output and a one-line reading per command naming the provider (for example, name servers `*.registrar-servers.com` indicate Namecheap), or states "unanswered" with the reason.
**Depends on:** none.

## Log
(empty)
