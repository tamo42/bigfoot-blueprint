# ICM FEEDBACK LOOP - BIGFOOT BLUEPRINT CONTROL PLANE

<LEAP_INSTRUCTION_SET>

  <META>
    <ID>bigfoot_feedback_loop.bleep</ID>
    <PURPOSE>To define the closed-loop learning engine, rule abstraction thresholds, and performance audits for the Bigfoot Blueprint workspace.</PURPOSE>
  </META>

  <TAB_7_FEEDBACK_GYROSCOPE>
    <RULE_INTEGRATION_PROTOCOL>
      - SYSTEM RULES BOOTSTRAP: Always load and parse the local `.system-rules.md` registry file on startup. Treat any rules registered (R-XXX) as mandatory execution guardrails.
    </RULE_INTEGRATION_PROTOCOL>

    <FEEDBACK_COLLECTION_CHANNELS>
      - SCRAPER AUDITS: Track data extraction failure rates (e.g. registry pagination breaks, PDF parsing failures, rate limits).
      - ENRICHMENT PERFORMANCE: Audit LLM outputs for response format conformity, hallucination rates, and profile accuracy.
      - CONVERSION RATE OPTIMIZATION (CRO): Monitor click-to-lead and claim rates across location hubs.
    </FEEDBACK_COLLECTION_CHANNELS>

    <RULE_ABSTRACTION_CONTROL>
      - ERROR ADAPTATION: If a scraper parsing bug, geocoding exception, or enrichment prompt drift is corrected manually 3-5 times, abstract the fix into a permanent rule (R-XXX) in `.system-rules.md`.
      - CORE RULES REGISTRY:
        - R-101: Never run geocoding APIs without local cache layers to prevent redundant coordinate calls.
        - R-102: Enrichments using Gemini 2.5 must use strict JSON schemas (structured output) to prevent parsing errors on special characters.
        - R-103: When deploying new directory subdomains, they must follow the format `niche-city.com` or `niche-state.com` and must be cataloged in `/02-workbench/nhq-bigfoot-blueprint/directory-registry.md` before going live.
    </RULE_ABSTRACTION_CONTROL>
  </TAB_7_FEEDBACK_GYROSCOPE>

</LEAP_INSTRUCTION_SET>
