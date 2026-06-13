import os
import sys
import json
import argparse
import requests
from pathlib import Path

# Load dotenv manually to support workspace-level .env files
def load_dotenv():
    # Look for .env in the root directory
    root_dir = Path(__file__).resolve().parents[3]
    env_path = root_dir / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

load_dotenv()

APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

def get_cache_path(query):
    # Normalize query for filename
    clean_query = "".join(c if c.isalnum() else "-" for c in query.lower())
    clean_query = "-".join(filter(None, clean_query.split("-")))
    
    # Path to cache folder
    script_dir = Path(__file__).resolve().parent
    cache_dir = script_dir.parent / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{clean_query}_raw.json"

def fetch_from_apify(query, country, lang):
    if not APIFY_API_TOKEN:
        print("Error: APIFY_API_TOKEN not found in environment variables or .env file.")
        sys.exit(1)
        
    print(f"Calling Apify Google Search Scraper actor for query: '{query}'...")
    
    url = f"https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items?token={APIFY_API_TOKEN}"
    payload = {
        "queries": query,
        "maxPagesPerQuery": 1,
        "resultsPerPage": 10,
        "countryCode": country.lower(),
        "languageCode": lang.lower()
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Apify: {e}")
        if 'response' in locals() and response is not None:
            print(f"Response content: {response.text}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Google search PAA crawler and cache manager (AnswerThePublic substitute).")
    parser.add_argument("--query", required=True, help="Target search query (e.g. 'septic pumping')")
    parser.add_argument("--region", default="US", help="Target region/country code (default: US)")
    parser.add_argument("--lang", default="EN", help="Target language code (default: EN)")
    
    args = parser.parse_args()
    
    cache_file = get_cache_path(args.query)
    
    # Check cache first
    if cache_file.exists():
        print(f"Loading search results from local cache: {cache_file.name}")
        with open(cache_file, "r") as f:
            data = json.load(f)
    else:
        # Fetch fresh data
        data = fetch_from_apify(args.query, args.region, args.lang)
        
        # Save to cache
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved results to local cache: {cache_file.name}")
        
    # Print summary of results
    print(f"\nSuccessfully retrieved search data for query: '{args.query}'")
    if isinstance(data, list) and len(data) > 0:
        item = data[0]
        if "peopleAlsoAsk" in item:
            paa = item["peopleAlsoAsk"]
            print(f"Found {len(paa)} 'People Also Ask' questions:")
            for p in paa:
                print(f"  - Question: {p.get('question')}")
                ans = p.get('answer') or 'N/A'
                print(f"    Answer: {ans[:200]}...")
        else:
            print("No 'People Also Ask' box was present on the Google Search page for this query.")
            print("Top level keys in dataset item:")
            for k in list(item.keys())[:10]:
                print(f"  - {k}")
    else:
        print("Warning: Retrieved data is empty or not in expected list format.")

if __name__ == "__main__":
    main()
