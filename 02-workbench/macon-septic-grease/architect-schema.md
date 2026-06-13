# Database Schema & Architecture: Macon Septic & Grease (`02-SEPTIC`)

This document outlines the SQLite database schema design for the `02-SEPTIC` directory database (`data/directory.sqlite`).

---

## 🗄️ SQLite Table Structure: `installers_haulers`

The directory uses a single primary table named `installers_haulers` to store company data, reviews, classification flags, and enriched AEO content.

```sql
CREATE TABLE installers_haulers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    place_id TEXT UNIQUE,
    address TEXT,
    city TEXT DEFAULT 'Macon',
    state TEXT DEFAULT 'GA',
    zip_code TEXT,
    phone TEXT,
    website_url TEXT,
    latitude REAL,
    longitude REAL,
    google_rating REAL DEFAULT 0.0,
    google_review_count INTEGER DEFAULT 0,
    reviews_json TEXT DEFAULT '[]', -- Array of review text snippets
    license_no TEXT,
    license_status TEXT DEFAULT 'Unverified', -- Active, Inactive, Unverified
    permit_expiration TEXT,
    specialty_grease_trap INTEGER DEFAULT 0, -- Boolean: 0 or 1
    specialty_septic_pump INTEGER DEFAULT 0, -- Boolean: 0 or 1
    specialty_riser_install INTEGER DEFAULT 0, -- Boolean: 0 or 1
    specialty_line_jetting INTEGER DEFAULT 0, -- Boolean: 0 or 1
    specialty_inspections INTEGER DEFAULT 0, -- Boolean: 0 or 1
    specialty_emergency_dispatch INTEGER DEFAULT 0, -- Boolean: 0 or 1
    specialties_crawled INTEGER DEFAULT 0, -- Boolean: 0 or 1 (Crawler finished)
    profile_bio TEXT, -- 200-400 words enriched overview
    faq_json TEXT DEFAULT '[]', -- Array of 20 local Q&As in JSON format
    speakable_bio TEXT, -- CSS selector target block text
    claimed INTEGER DEFAULT 0 -- Boolean: 0 or 1
);
```

---

## 📋 JSON Schema Formats for Columns

### `reviews_json`
Stores the top 3 review text strings retrieved from the Places Details API.
```json
[
  "They arrived on time and pumped my septic tank within an hour. Excellent service!",
  "Highly professional. Helped clean out our commercial kitchen grease trap without any mess.",
  "Taylor Septic solved our backup issue quickly and charged a fair price."
]
```

### `faq_json`
Enriched JSON array containing 20 local regulatory Q&As for the specific business profile.
```json
[
  {
    "question": "Does this provider service municipal grease traps under Macon Water Authority rules?",
    "answer": "Yes, they are permitted to service and pump commercial interceptors in compliance with the MWA's quarterly inspection guidelines."
  },
  {
    "question": "What is the 25% rule for grease traps?",
    "answer": "The Macon Water Authority requires commercial grease interceptors to be pumped when the Fats, Oils, and Grease (FOG) layer and Food Solids layer reach 25% of the total liquid capacity, or quarterly, whichever occurs first."
  }
]
```
