# Georgia Grease Trap: Offsite & Infrastructure Reference

This reference index documents the off-user-facing infrastructure, tracking mechanisms, third-party integrations, and verification frameworks established for `georgiagreasetrap.com` (Georgia Grease Trap).

---

## 1. Analytics & Tracking (Umami)

Umami Analytics is integrated to measure user interactions and micro-conversion events without collecting personal data.

- **Umami Snippet**: Embedded globally in the page `<head>` via [Layout.astro](file:///C:/Users/tamo4/git/bigfoot-sites/georgiagreasetrap.com/src/layouts/Layout.astro).
- **Event Registry**:
  - `click-claim-profile`: Tracks when a contractor initiates a profile claim request. Passes `{ hauler: "Hauler Name" }` metadata.
  - `click-verify-capability`: Tracks when a user/owner attempts to verify a missing credential (e.g., COI limits, SOS status, specialty service). Passes `{ hauler: "Hauler Name", field: "field_name" }`.
  - `calculate-intervals`: Tracks FOG compliance calculator submissions.
  - `search-click`: Tracks autocomplete clicks in the location search bar.

---

## 2. Crawlability & Metadata Files

Several text and XML documents are generated dynamically during the `npm run build` process to guide search engines, crawler bots, and AI agents.

- **Sitemap (`sitemap.xml`)**: Index of all 318 generated static URLs (including all county pages and contractor details). Auto-generated at the root.
- **Search Engine Directives (`robots.txt`)**: Located at the root. Directs search engines to crawl all pages and points directly to the sitemap:
  ```text
  User-agent: *
  Allow: /

  Sitemap: https://georgiagreasetrap.com/sitemap.xml
  ```
- **AI Agent Context (`llms.txt`)**: Auto-generated text context descriptor at the root of the site, providing semantic data structure pointers for large language model parsers.

---

## 3. Google Search Console (GSC)

- **Verification**: Verified under the personal `tamo42` Search Console account.
- **Sitemap Submission**: `https://georgiagreasetrap.com/sitemap.xml` has been submitted to GSC to accelerate indexing of county and contractor listing hubs.

---

## 4. Email Claims & GHL Integration

All verification, claim, and quote actions resolve to specific mailto triggers.

- **Sender Target**: `claims@georgiagreasetrap.com`
- **Claim Action**: Initiates email claims automation template in GoHighLevel (GHL) managed by Rodrigo.
- **Compliance Address**: Physical address used for compliance and legal context:
  ```text
  2302 Parklake Dr NE Ste 675, Atlanta, GA 30345
  ```
