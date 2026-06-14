# ICM MECHANISM BLUEPRINT - BIGFOOT BLUEPRINT CONTROL PLANE

<LEAP_INSTRUCTION_SET>

  <META>
    <ID>bigfoot_mechanism_blueprint.bleep</ID>
    <PURPOSE>To define the 4-phase state machine and transition protocols for launching and running Bigfoot directory properties.</PURPOSE>
  </META>

  <TAB_5_STATE_MACHINE>
    <STATE_MAP>
      - CURRENT_STATE: STATE_01_SELECTION_VIABILITY
      - TRANSITION_PATHS:
          STATE_01_SELECTION_VIABILITY -> STATE_02_AGENTIC_DISCOVERY
          STATE_02_AGENTIC_DISCOVERY -> STATE_03_ENGINEERING_PIPELINE
          STATE_03_ENGINEERING_PIPELINE -> STATE_04_ANTIGRAVITY_DEPLOYMENT
    </STATE_MAP>

    <STATE_01_SELECTION_VIABILITY>
      <INSTRUCTIONS>
        1. Identify fragmented B2B/niche opportunities.
        2. Evaluate the niche against Avatar Adjacency (R-115) and the Scale vs. Frequency Equation (R-116).
        3. Determine go/no-go based on rapid data availability (can we get 2,000+ centralized records quickly?).
        4. Run programmatic Keyword Research via the AnswerThePublic API to capture real-world search queries.
        5. Compile the Search Intent Map (e.g. p1_keyword_intent_map.md) to define target database columns, scraper capability tags, and calculators.
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Niche passes viability scorecard, keyword crawls complete, and Search Intent Map written.</TRANSITION_CRITERIA>
    </STATE_01_SELECTION_VIABILITY>

    <STATE_02_AGENTIC_DISCOVERY>
      <INSTRUCTIONS>
        1. Run the Architect bot process to define the 7-Layer Hierarchy, target data types, and AEO/SEO structures (geographic/use-case multiplexers).
        2. Configure the scraper schema (Apify, Playwright, or direct crawler) to target the custom capability fields and tags defined in the Search Intent Map.
        3. Design and specify the un-gated Hormozi/Cialdini value-adding reciprocity tools (e.g. unified calculators) above the fold, mapping calculator tabs to keyword intent profiles.
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Architecture mapped, scraper schema configured from Intent Map, and reciprocity tools designed.</TRANSITION_CRITERIA>
    </STATE_02_AGENTIC_DISCOVERY>

    <STATE_03_ENGINEERING_PIPELINE>
      <INSTRUCTIONS>
        1. Deploy the configured scrapers to harvest public registries (parsing PDFs locally via Python script - R-108).
        2. Clean listings data and geocode records using a local caching layer to avoid redundant API fees (R-101).
        3. Execute Gemini LLM enrichment loops natively inside the Antigravity IDE to generate Q&A blocks answering the niche's Top 20 Questions.
        4. Compile all cleaned and enriched data into a local SQLite database (directory.sqlite).
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Database is 100% enriched, cleaned, geocoded, and compiled locally as SQLite.</TRANSITION_CRITERIA>
    </STATE_03_ENGINEERING_PIPELINE>

    <STATE_04_ANTIGRAVITY_DEPLOYMENT>
      <INSTRUCTIONS>
        1. Spin up a dedicated sister folder/repository natively within the Antigravity IDE workspace.
        2. Implement the frontend framework (Astro or Next.js) and push staging data to Supabase.
        3. Generate non-user-facing SEO/AEO optimization layers (XML sitemaps, JSON-LD schema, `llms.txt`).
        4. Hook the repository to Railway through GitHub for immediate live deployment.
      </INSTRUCTIONS>
      <TRANSITION_CRITERIA>Directory is live, optimized, and ready for Stage 1 validation tracking.</TRANSITION_CRITERIA>
    </STATE_04_ANTIGRAVITY_DEPLOYMENT>
  </TAB_5_STATE_MACHINE>

</LEAP_INSTRUCTION_SET>
