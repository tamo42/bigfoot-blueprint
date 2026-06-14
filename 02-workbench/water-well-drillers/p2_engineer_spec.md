# Engineer Bot Pipeline Spec

*Generated from the Engineer Bot for the Water Well Drillers Apify Actor.*

## Block A — Actor Spec

```text
Actor name:      water-well-drillers-enrichment-actor
Niche:           water well drillers and pump maintenance specialists
Listing types:   well-driller, pump-specialist
Total fields:    98
LLM model:       gemini-2.5-flash
SDK spec:        confirmed current

KV Store name:   water-well-drillers-data
Input KV key:    water-well-drillers_seed.csv
Output KV key:   water-well-drillers_enriched.csv
Pending KV key:  water-well-drillers_pending.csv
```

## Block B — Question Selection

📋 **7 Phase 1 Questions** — water well drillers and pump maintenance specialists

### Tier 1 (Universal):
* **Q1.** What are the hours of operation? — hours
* **Q2.** Is there a fee to use this? — cost/fees
* **Q3.** What is this place and what can I find here? — accepted/available
* **Q4.** Do I need an appointment or can I walk in? — appointment/registration
* **Q5.** How do I get there and where do I park? — location/directions

### Tier 2 (Niche-Specific):
* **Q6.** Do they provide guaranteed 24/7 emergency dispatch support? — This answers the most critical, high-urgency question for rural homeowners facing a sudden total loss of running water.
* **Q7.** Do they handle local water permits and state regulatory filings? — This clarifies compliance and bureaucratic management for homeowners planning a major structural well installation.
