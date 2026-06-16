# Bigfoot Blueprint: Newsjacking & Regulatory Engine Specification

**Status:** Draft / Active Specification
**Layer:** Component Blueprint
**Purpose:** Defines the automated daily pipeline for ingesting, evaluating, and publishing newsjacking content and regulatory tracking across all Bigfoot directories.

---

## 1. Core Architecture: The "Pincer Strategy"

The Newsjacking engine utilizes a two-pronged "Pincer" approach to ensure both hyper-local niche coverage and macro-trend capitalization, without overwhelming API or LLM token limits.

### Prong A: The Micro Pull (Bottom-Up)
This pipeline actively hunts for highly specific industry news that general feeds ignore.

*   **Mechanism:** Queries the Google News RSS endpoint using 3-5 highly optimized Boolean strings derived from the directory's SEO entity research.
    *   *Example Query:* `"real estate" AND ("closing" OR "escrow" OR "title insurance")`
*   **Pipeline Execution:**
    1.  Fetch RSS results filtered for the last 24 hours (`when:1d`).
    2.  Decode Google News tracker URLs (`CBMi...`) into raw publisher URLs using `googlenewsdecoder`.
    3.  Extract pure article text using `trafilatura` to bypass ads and layout junk.
    4.  Discard articles behind hard paywalls or bot blockers.
    5.  Pass the successful full-text extractions to the Generation LLM to draft the post.

### Prong B: The Macro Synthesizer (Top-Down)
This pipeline captures viral, top-of-mind national news and searches for a niche-specific angle.

*   **Mechanism:** Queries the predefined Google News Topic segments (NATION, BUSINESS, TECHNOLOGY, SCIENCE) to gather the top ~40-60 macro headlines of the day.
*   **The Triage Matrix (Air Traffic Controller):**
    *   The raw full text is **not** downloaded.
    *   A single LLM prompt ingests the 50 Headlines + Summaries and the array of active Bigfoot Avatars.
    *   *Prompt Directive:* "Identify any macro news story that presents a strong newsjacking opportunity for any of our niches. Return a JSON array mapping the `Headline` to the `Niche` with a proposed 1-sentence `Angle`."
    *   If a match is found, the system triggers Prong A's extraction and generation pipeline for that specific article and niche.

---

## 2. Volume, Output, and Placement Rules

To preserve directory authority and prevent a "spammy" appearance, strict volume limits are enforced.

*   **The Rule of One:** The system will generate and publish a maximum of **one** long-form newsjacking blog post per day, per directory. The LLM selects the story with the highest relevance score.
*   **Newsletter Queue:** If the Triage Matrix or Micro Pull finds multiple highly relevant stories in a single day, the excess stories are not published as blogs. They are saved to a `newsletter_queue` database to be aggregated into a weekly email (Format: "1 Deep Dive + 3 Quick Hits").
*   **Astro Frontend Placement:**
    *   **The News Section:** Full posts live in a dedicated `/news` or `/insights` Astro content collection for SEO indexing.
    *   **The Homepage:** Adhering to the *Reciprocity Prioritization* rule, the calculator/evaluation tool remains above the fold. The homepage will only feature a sleek "Latest Industry Insight" widget below the fold, linking to the most recent post.

---

## 3. Regulatory Tracking & Defamation Safety Protocol

For specific niches (e.g., Closing Attorneys, CPAs, Contractors), tracking disciplinary actions by regulatory bodies provides immense user value. However, the risk of defamation via AI hallucination is critical. 

**Strict Safety Protocol:**
1.  **AI is Banned from Regulatory Flagging:** LLMs are strictly forbidden from reading news articles to apply disciplinary flags to directory listings. 
2.  **Deterministic Sourcing Only:** Disciplinary data must be scraped deterministically from the official public feeds of the governing body (e.g., State Bar official XML feed, State Licensing Board API).
3.  **Strict Primary Key Matching:** The script must match the regulatory action to the directory listing using their **License Number** or **Bar Number**. Matching on Name alone is strictly prohibited to avoid false positives.
4.  **Clinical Reporting Only:** If a primary key match is confirmed, the system applies a visual flag component to the listing. The copy must be hardcoded and non-editorialized:
    *   *Template:* "Notice: A public disciplinary action was recorded by the [Governing Body] on [Date]. [Click here to view the official public record]."

---

## 4. Required Technologies & Libraries

*   **Syndication:** `xml.etree.ElementTree`, `urllib`
*   **URL Decoding:** `googlenewsdecoder` (Required to bypass Google News tracking walls).
*   **Text Extraction:** `trafilatura` (Machine learning-based main text extraction).
*   **LLM Engine:** Google Gemini (For Triage Matrix and Post Generation).
*   **Database:** SQLite (For caching daily news pulls and managing the `newsletter_queue`).
