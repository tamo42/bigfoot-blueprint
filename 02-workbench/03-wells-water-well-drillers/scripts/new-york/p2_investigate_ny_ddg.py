from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    results = [r for r in ddgs.text('site:dec.ny.gov "Water Well Contractor Search Tool"', max_results=5)]
    print(json.dumps(results, indent=2))
