# Technical Reference: uswelldrillers.com Canonicalization (seed input for every phase)

Facts, paths, commands and code a fresh agent needs. Facts were verified 2026-11-02 unless marked **UNVERIFIED**. Coordinating PRD: `p4_canonical_trailing_slash_plan.md` (same folder). If this file and live reality disagree, trust reality, log the difference in the phase log, and fix this file in the same write-back.

## 1. Glossary
- **Canonical tag:** `<link rel="canonical" href="...">` in a page's `<head>`. It tells Google which URL is the one to index when several URLs return the same page.
- **Trailing slash:** the final `/` in a URL path (`/ga/` has one, `/ga` does not).
- **Apex domain:** `uswelldrillers.com` (no `www.`). **www variant:** `www.uswelldrillers.com`.
- **GSC:** Google Search Console, property `uswelldrillers.com`. Only Neal can log in; agents cannot read it. Anything from GSC arrives as exports or screenshots Neal provides.
- **Site repo:** the deployed Astro website. **Control-plane repo:** this repo, `nhq-bigfoot-blueprint`, which holds specs, plans and cross-site scripts.

## 2. Repos, paths and shell
| Thing | Value |
| :-- | :-- |
| Site repo | `C:\Users\tamo4\git\bigfoot-sites\uswelldrillers.com` (remote `https://github.com/tamo42/uswelldrillers.com.git`, branch `master`) |
| Control-plane repo | `C:\Users\tamo4\git\nhq-bigfoot-blueprint` |
| Project docs (this folder) | `C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\` |
| Evidence folder (create if absent) | `<project docs>\p4_canonical_evidence\` |
| Site stack | Astro `^6.4.7`, Tailwind 4, `better-sqlite3`, `@astrojs/sitemap`; Node `>=22.12` (local Node is v24.16.0) |
| Site data | `water_well_directory.sqlite` at the site repo root; accessed by `src/lib/db.ts` |
| Hosting | Railway, deployed from GitHub on push (registry row `03-WELLS`). Response header `Server: railway-hikari` = Railway static host |
| Shell | Windows 11; Git Bash and PowerShell both available. Commands below are Git Bash unless marked |

Site commands (run inside the site repo): `npm install` (only if `node_modules` is missing), `npm run build` (writes `dist/`, which is git-ignored), `npm run preview` (serves `dist/` on `http://localhost:4321`; stop it when done).

Repo-boundary rule (02_context_boundary.bleep.md PUSH BOUNDARY): commit or push only inside ONE repo at a time. Never run git commands that touch `neal-os`, `tax-sherpa`, `resilient-roots` or other sites. Never commit credentials or `.env` files.

## 3. URL policy (decided by Neal, 2026-11-02)
Every page has exactly one URL: `https://uswelldrillers.com/<path>/`: https, apex (no www), **trailing slash on every page**. The home page is `https://uswelldrillers.com/`. Files with an extension (`/search-index.json`, `/favicon.svg`, `/robots.txt`, `/sitemap-index.xml`, `/llms.txt`) never get a trailing slash. Query strings and fragments follow the slash: `/search/?q=pump`, `/va/accomack-well-pump-troubleshooting/#tab-diag`.

## 4. Evidence the problem exists (Google Search Console, exported 2026-11-02, data to 2026-10-22)
| Metric | Value |
| :-- | :-- |
| Indexed / Not indexed | 6,359 / 13,240 |
| Duplicate without user-selected canonical | **6,066** (rising) |
| Discovered, currently not indexed | 6,707 |
| Crawled, currently not indexed | 464 |
| Page with redirect / Server error (5xx) | 2 / 1 |
| Sitemap | `https://uswelldrillers.com/sitemap-index.xml` → `sitemap-0.xml`; 9,420 URLs, all with trailing slash |
| Clicks by month Jun, Jul, Aug, Sep, Oct 2026 | 15, 140, 215, 443, 511 |
| GSC Pages export | lists the same page as `/x`, `/x/` and `www.` variants |
Source files: `C:\Users\tamo4\Downloads\uswelldrillers.com-*` (screenshots `search_console-1..3.png`, zips `Coverage` and `Performance-on-Search`).

Verified in the repo and live:
1. `grep -ri canonical src` finds nothing: no page has a canonical tag.
2. `curl -s -o /dev/null -w "%{http_code}"` returns **200** for `https://uswelldrillers.com/contractors/dylan-dodgion-va`, the same with `/`, and `https://www.uswelldrillers.com/contractors/dylan-dodgion-va`. No redirects exist.
3. Internal links and JSON-LD `url` fields are written without a trailing slash (inventory in §7 and §8).

## 5. Site structure (for expected counts)
Astro file routes in `src/pages/`:
| Route file | URL produced | Approx. count |
| :-- | :-- | :-- |
| `index.astro` | `/` | 1 |
| `contractors/[slug].astro` | `/contractors/<slug>/` | 5,181 |
| `[state]/[county].astro` | `/<st>/<county>-county-well-drillers/` | 1,045 |
| `[state]/[county]-well-drilling-costs-and-permits.astro` | `/<st>/<county>-well-drilling-costs-and-permits/` | 1,045 |
| `[state]/[county]-well-pump-troubleshooting.astro` | `/<st>/<county>-well-pump-troubleshooting/` | 1,045 |
| `[state]/[county]-well-water-testing-and-smell.astro` | `/<st>/<county>-well-water-testing-and-smell/` | 1,045 |
| `[state]/index.astro` | `/<st>/` | about 40 |
| `news/index.astro`, `news/[slug].astro` | `/news/`, `/news/<id>/` | 1 + 2 |
| `drilling-cost-calculator`, `pump-diagnostics`, `water-quality-tester`, `water-softeners`, `iron-filtration-systems`, `hydrogen-sulfide-aeration`, `search` `.astro` | `/<name>/` | 7 |
| `search-index.json.ts` | `/search-index.json` (endpoint, not a page) | 1 file |
The June-July `dist/` held 9,417 HTML files. Phase 1 rebuilds and records the true baseline; later criteria compare against that number, not this table.

## 6. Code to add (Phase 2)
`astro.config.mjs` currently is:
```js
export default defineConfig({
  site: 'https://uswelldrillers.com',
  vite: { plugins: [tailwindcss()] },
  integrations: [sitemap()]
});
```
Add `trailingSlash: 'always'` and `build: { format: 'directory' }` as top-level keys.

`src/layouts/Layout.astro` frontmatter ends at line 13 (`const schemaString = ...`). Add below it:
```astro
const canonicalUrl = new URL(Astro.url.pathname, Astro.site).href;
```
and in `<head>`, directly after `<title>{title}</title>` (line 24):
```html
<link rel="canonical" href={canonicalUrl} />
<meta property="og:url" content={canonicalUrl} />
```
Do not add an override prop; YAGNI. Expected result for `/contractors/foo/`: `https://uswelldrillers.com/contractors/foo/`; for home: `https://uswelldrillers.com/`.
**UNVERIFIED:** that Astro 6 keeps `/search-index.json` working under `trailingSlash: 'always'` (file endpoints with an extension should be exempt). Phase 2 step 2.1 checks it. If it breaks, use `trailingSlash: 'always'` only if `/search-index.json` still builds; otherwise stop with outcome *scope changed*.

## 7. Link inventory (Phase 3). Every internal link below needs a trailing slash.
Static templates (rendered into HTML; step 3.1):
| File:line | Current | Becomes |
| :-- | :-- | :-- |
| `src/components/Header.astro:13,14` | `/drilling-cost-calculator`, `/pump-diagnostics` | add `/` |
| `src/components/Footer.astro:13-16, 23-25` | `/tx`,`/fl`,`/ga`,`/ca`, `/drilling-cost-calculator`, `/pump-diagnostics`, `/water-quality-tester` | add `/` |
| `src/components/LatestInsight.astro:24,34,40` | `/news/${latestPost.id}`, `/news` | add `/` |
| `src/pages/index.astro:144,158` | `/${s.code.toLowerCase()}` | add `/` |
| `src/pages/news/index.astro:28,36` | `/news/${post.id}` | add `/` |
| `src/pages/news/[slug].astro:19` | `/news` | `/news/` |
| `src/pages/[state]/index.astro:36` | `.../${...}-county-well-drillers` | add `/` |
| `src/pages/[state]/[county]-well-drilling-costs-and-permits.astro:175,250,257,262` | `-county-well-drillers`, `-well-pump-troubleshooting`, `-well-water-testing-and-smell` | add `/` |
| `src/pages/[state]/[county]-well-pump-troubleshooting.astro:212,326,333,338` | same pattern | add `/` |
| `src/pages/[state]/[county]-well-water-testing-and-smell.astro:188,286,293,298` | same pattern | add `/` |
| `src/pages/[state]/[county].astro:189,202,213` | `/contractors/${c.slug}` | add `/` |
Links to `/` (`src/pages/*.astro` and `news/[slug].astro:53`, Header:6) are already correct. `/#find-a-driller` (`pump-diagnostics.astro:169,223`) is correct. `tel:` and external links are untouched.

Script-embedded links (built in browser JavaScript, invisible in rendered anchors; step 3.2):
| File:line | Current | Becomes |
| :-- | :-- | :-- |
| `src/components/DirectorySearch.astro:75` | `/contractors/${item.slug}` | `/contractors/${item.slug}/` |
| `src/components/DirectorySearch.astro:83` | `/search?q=${...}` | `/search/?q=${...}` |
| `src/pages/search.astro:54` | `/contractors/${item.slug}` | add `/` |
| `src/components/UnifiedWellCalculator.astro:291,298` | `/${dynamicState}/${dynamicCounty}-well-pump-troubleshooting#${diagSelect.value}` | `...-well-pump-troubleshooting/#${...}` |
| `src/components/UnifiedWellCalculator.astro:293,300` | `/pump-diagnostics` | `/pump-diagnostics/` |
| `src/components/UnifiedWellCalculator.astro:334` | `/${dynamicState}/${dynamicCounty}-well-water-testing-and-smell` | add `/` |
| `src/components/UnifiedWellCalculator.astro:336` | `/water-quality-tester` | add `/` |
| `src/components/LocalGuideFunnel.astro:88` | `` `/${currentState}/${countyVal}${guideSuffix}` `` | append `/` after `${guideSuffix}` |
Also read `UnifiedWellCalculator.astro:340-344` for any further links (grep showed `href` hits on 340, 342, 344 that were cut off). Line numbers may drift; search by the "Current" text. The path checks at `UnifiedWellCalculator.astro:351-355` use `includes('pump-diagnostics')`, which keep working with a slash.

## 8. JSON-LD inventory (step 3.3)
| File:line | Current `url` | Becomes |
| :-- | :-- | :-- |
| `src/pages/index.astro:46,54` | `https://uswelldrillers.com` | `https://uswelldrillers.com/` |
| `src/pages/index.astro:64` | `https://uswelldrillers.com/drilling-cost-calculator` | add `/` |
| `src/pages/index.astro:73` | `https://uswelldrillers.com/pump-diagnostics` | add `/` |
| `src/pages/[state]/[county].astro:92` | `` `https://uswelldrillers.com/contractors/${c.slug}` `` | add `/` |
`@id` values (`https://uswelldrillers.com/#organization`, `#website`) are identifiers; leave them. `contractors/[slug].astro` builds a LocalBusiness schema (line ~38-76) with no `url` field; leave it.

## 9. Audit script spec (`scripts/seo_canonical_audit.py`, Phase 1)
Location: `C:\Users\tamo4\git\nhq-bigfoot-blueprint\scripts\seo_canonical_audit.py`. Python 3 standard library only. Reusable for any Astro directory site.
CLI: `python scripts/seo_canonical_audit.py --dist <path to dist> --site https://uswelldrillers.com [--out <report.txt>] [--max-examples 10]`.
It walks every `*.html` under `--dist`. A file `dist/a/b/index.html` is the page `/a/b/`; `dist/index.html` is `/`. It reports a count and up to `--max-examples` examples for each check, and exits **0 only if every check passes**, otherwise 1.
| Check | Fails when |
| :-- | :-- |
| C1 canonical present | a page has 0 or more than 1 `<link rel="canonical">` |
| C2 canonical correct | canonical href != `--site` + the page's own path (including trailing slash, https, no www) |
| C3 sitemap parity | the set of URLs in `dist/sitemap-0.xml` (follow `dist/sitemap-index.xml`) != the set of page canonicals. Report both directions |
| C4 anchors | any `<a href>` that is on-site (starts with `/` but not `//`, or starts with `--site`) has a path with no extension and no trailing slash. Ignore `tel:`, `mailto:`, `#only`, external hosts |
| C5 script-embedded links | in inline `<script>` text and non-JSON-LD script text, any string like `href="/..."`, `` href=`/...` `` or `href='/...'` whose path (before `?` or `#`) lacks a trailing slash and has no extension. Report file and the matched text |
| C6 link targets exist | an on-site anchor path does not match a `dist` page or file |
| C7 JSON-LD urls | any `url` value in an `application/ld+json` block that starts with `--site` has a path with no extension and no trailing slash; also fails if a block is not valid JSON |
Print a summary table (check, pass/fail, count) first, then examples. Document it in `scripts/README.md` using the R-131 structure (Script Name, What it does, Why it does it, Inputs, Outputs). Test fixtures live in `scratch/` (R-113), never in the repo root.

## 10. Live verification commands (Phases 2, 3, 5)
Sample set (build it once in Phase 1 into `p4_canonical_evidence/sample-urls.txt`, 20 lines, all `https://uswelldrillers.com/...` with trailing slash): `/`, `/tx/`, one county page of each of the four county templates, three `/contractors/<slug>/`, `/news/`, one `/news/<id>/`, the six tool pages, `/search/`.
Per URL: `curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" <url>` (expect `200` with empty redirect), and `curl -s <url> | grep -o '<link rel="canonical"[^>]*>'` (expect exactly one, href equal to the URL).
Redirect matrix (Phase 5): for each of 5 URLs test `https://uswelldrillers.com/p/`, `https://uswelldrillers.com/p`, `https://www.uswelldrillers.com/p/`, `https://www.uswelldrillers.com/p` and `http://uswelldrillers.com/p/`. Exactly one (apex, https, slash) returns 200; each other returns one `301` whose `Location` is that URL (no chains: `curl -sIL` shows two status lines at most).
Performance: `npx lighthouse https://uswelldrillers.com/ --only-categories=performance --quiet --chrome-flags="--headless" --output=json --output-path=<file>`; repeat for one `/contractors/<slug>/`. Needs Chrome installed. Blueprint threshold (STATE_04): performance >= 90.
Analytics: the page source must still contain `https://umami-production-26bd.up.railway.app/script.js` (blueprint STATE_04 item 6).
Schema: Google Rich Results Test (`https://search.google.com/test/rich-results`) is a human look by Neal.

## 11. Rollback
- Code phases (2, 3): `git revert <commit>` in the site repo, push; Railway redeploys the previous behavior in minutes. Nothing in these phases changes data.
- Redirects (5): restore the previous DNS or host setting; record the old value in the phase log before changing.
- Search Console actions (6) are not reversible but are harmless (resubmitting a sitemap, requesting indexing).

## 12. Known unknowns
1. DNS provider for `uswelldrillers.com` (Neal: "probably Namecheap or GHL"). Phase 4 finds out. `nslookup -type=NS uswelldrillers.com` shows the name servers.
2. Whether Railway's static host can issue redirects. Phase 4 finds out from Railway docs.
3. Whether the stale-looking June/July `dist/` equals what is live. Phase 1 rebuilds and compares against the live sitemap (9,420).
4. Google's reaction time. Canonical changes typically take weeks to reflect; thresholds in the PRD are proposals.

## 13. Out of scope observations (log, do not fix)
- `Layout.astro` has no `<meta name="description">` prop; page descriptions are absent site-wide.
- 6,707 "Discovered, not indexed" pages may be thin programmatic content (R-119). Separate project.
- The same duplicate problem is likely on georgiagreasetrap.com and gaclosinglawyers.com (which also has a duplicate `[county]/[slug]` route). Separate projects, after this fix is proven.
