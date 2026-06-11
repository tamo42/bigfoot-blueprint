# ICM MECHANISM BLUEPRINT - BIGFOOT BLUEPRINT CONTROL PLANE

<LEAP_INSTRUCTION_SET>

  <META>
    <ID>bigfoot_mechanism_blueprint.bleep</ID>
    <PURPOSE>To define the 4-phase state machine and transition protocols for launching and running Bigfoot directory properties.</PURPOSE>
  </META>

  <TAB_5_STATE_MACHINE>
    <STATE_MAP>
      - CURRENT_STATE: STATE_01_IDENTIFY_SCHEMA
      - TRANSITION_PATHS:
          STATE_01_IDENTIFY_SCHEMA -> STATE_02_INGEST_ENRICH
          STATE_02_INGEST_ENRICH -> STATE_03_BUILD_TEMPLATE
          STATE_03_BUILD_TEMPLATE -> STATE_04_DEPLOY_MONETIZE
    </STATE_MAP>

    <STATE_01_IDENTIFY_SCHEMA>
      <INSTRUCTIONS>
        1. Identify fragmented B2B/niche opportunities with public licensing registries (State Bar, EPA, SOS, municipal registers).
        2. Perform keyword research using AnswerThePublic to extract high-volume "head" questions.
        3. Define the directory's standard schema (e.g. License Number, Status, Coordinates, Phone, Principal Owner, Insurance, Q&A fields).
        4. Develop a geo-intent multiplexing plan to combine head questions with target geographic variables.
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Target registry is identified, keywords mapped, and database schema is finalized.</TRANSITION_CRITERIA>
    </STATE_01_IDENTIFY_SCHEMA>

    <STATE_02_INGEST_ENRICH>
      <INSTRUCTIONS>
        1. Run scraping scripts or Apify actors to crawl the target registry, outputting a raw CSV/JSON.
        2. Geocode addresses using a free geocoding API to append Latitude and Longitude coordinates.
        3. Run programmatic LLM enrichment script (`gabar-enricher.py` or equivalent) inside the Antigravity IDE using Google AI Ultra (Gemini 2.5 Flash / Pro).
        4. For each business profile, prompt Gemini 2.5 to answer the niche's Top 20 Questions.
        5. Clean and store the enriched profiles inside the local `directory.sqlite` file.
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>The database is 100% enriched, and `directory.sqlite` is saved and committed to Git.</TRANSITION_CRITERIA>
    </STATE_02_INGEST_ENRICH>

    <STATE_03_BUILD_TEMPLATE>
      <INSTRUCTIONS>
        1. Inject `directory.sqlite` into the Astro project data layer.
        2. Configure brand styles (colors, fonts, name) inside Astro token files.
        3. Build the static site (`npm run build`) generating optimized HTML for every city hub and listing detail page.
        4. Verify that:
           - Interactive calculators load and operate correctly in the primary viewport.
           - Flat URL semantic silo links are present (Pillar <-> Child -> Listings).
           - JSON-LD schemas (FAQPage speakable selectors, ItemList, LocalBusiness) exist in the head.
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Site builds with 0 errors, Lighthouse performance is 100/100, and local validation passes.</TRANSITION_CRITERIA>
    </STATE_03_BUILD_TEMPLATE>

    <STATE_04_DEPLOY_MONETIZE>
      <INSTRUCTIONS>
        1. Push the Astro project to a dedicated private GitHub repository and link it to Vercel/Netlify for free hosting.
        2. Register the domain/subdomain and link it to the GSC (Google Search Console) project board.
        3. Log the site launch in `/02-workbench/nhq-bigfoot-blueprint/directory-registry.md`.
        4. Track Stage 1 validation KPIs (Indexing >60%, Impressions >500/week, Clicks >20/week, Claims >2).
        5. If triggers are met:
           - Migrate SQLite data to multi-tenant Supabase partitioned by `directory_id`.
           - Enable dynamic reviews, claims routing, and certificate of insurance (COI) uploads.
           - Trigger outreach campaigns via GoHighLevel using Cialdini's Persuasion Playbook (Loss Aversion, Conquest Ads, Reciprocity via personalized Loom videos).
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Directory is live, GSC is tracked, and Stage 2 migration is executed once validation triggers fire.</TRANSITION_CRITERIA>
    </STATE_04_DEPLOY_MONETIZE>
  </TAB_5_STATE_MACHINE>

</LEAP_INSTRUCTION_SET>
