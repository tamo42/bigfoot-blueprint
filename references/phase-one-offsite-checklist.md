# Phase One Deployment: Offsite & Infrastructure Checklist

This reference index documents the off-user-facing infrastructure, tracking mechanisms, third-party integrations, and verification frameworks that must be established before launching a Phase One Bigfoot Blueprint directory site.

---

## 1. Analytics & Tracking (Umami)

Umami Analytics is integrated to measure user interactions and micro-conversion events without collecting personal data.

- **Umami Snippet**: Ensure the snippet is embedded globally in the page `<head>` via the main layout file (e.g., `Layout.astro`).
- **Event Registry** (Customize per project):
  - `click-claim-profile`: Tracks when a business initiates a profile claim request. Pass `{ entity: "Business Name" }` metadata.
  - `click-verify-capability`: Tracks when a user/owner attempts to verify a missing credential (e.g., license status, specific capabilities). Pass `{ entity: "Business Name", field: "field_name" }`.
  - `calculate-[tool-name]`: Tracks specific calculator or interactive tool submissions.
  - `search-click`: Tracks autocomplete clicks in the location search bar.

---

## 2. Crawlability & Metadata Files

Several text and XML documents should be generated dynamically during the `npm run build` process to guide search engines, crawler bots, and AI agents.

- **Sitemap (`sitemap.xml`)**: Index of all generated static URLs (including all geography pages and business details). Auto-generated at the root.
- **Search Engine Directives (`robots.txt`)**: Located at the root. Directs search engines to crawl all pages and points directly to the sitemap:
  ```text
  User-agent: *
  Allow: /

  Sitemap: https://{{YOUR_DOMAIN.COM}}/sitemap.xml
  ```
- **AI Agent Context (`llms.txt`)**: Auto-generated text context descriptor at the root of the site, providing semantic data structure pointers for large language model parsers.

---

## 3. Google Search Console (GSC)

- **Verification**: Verify the domain under your designated Search Console account (e.g., via DNS TXT record).
- **Sitemap Submission**: Submit `https://{{YOUR_DOMAIN.COM}}/sitemap.xml` to GSC to accelerate indexing of regional and business listing hubs.

---

## 4. Email Claims & CRM Integration

All verification, claim, and quote actions should resolve to specific triggers for CRM automation (e.g., GoHighLevel).

- **Sender Target**: `claims@{{YOUR_DOMAIN.COM}}` (or a similar standardized alias).
- **Claim Action**: Initiates email claims automation template in the CRM.
- **Compliance Address**: Ensure the correct physical address is used for compliance and legal context in footer and email footers:
  ```text
  [Your Central Compliance/Physical Address]
  ```
