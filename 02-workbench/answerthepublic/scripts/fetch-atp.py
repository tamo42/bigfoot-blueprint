import os
import sys
import json
import time
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

ANSWERTHEPUBLIC_API_KEY = os.environ.get("ANSWERTHEPUBLIC_API_KEY")

def get_cache_path(query, region, lang):
    # Normalize query for filename
    clean_query = "".join(c if c.isalnum() else "-" for c in query.lower())
    clean_query = "-".join(filter(None, clean_query.split("-")))
    
    # Path to cache folder
    script_dir = Path(__file__).resolve().parent
    cache_dir = script_dir.parent / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{clean_query}_{region.lower()}_{lang.lower()}_raw.json"

def get_report_path(query, region, lang):
    # Normalize query for filename
    clean_query = "".join(c if c.isalnum() else "-" for c in query.lower())
    clean_query = "-".join(filter(None, clean_query.split("-")))
    
    # Path to reports folder
    script_dir = Path(__file__).resolve().parent
    reports_dir = script_dir.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir / f"{clean_query}_{region.lower()}_{lang.lower()}_summary.md"

def write_markdown_report(query, region, lang, suggestions):
    report_file = get_report_path(query, region, lang)
    
    # Group suggestions by source_name
    groups = {}
    for sug in suggestions:
        src = sug.get("source_name", "unknown")
        groups.setdefault(src, []).append(sug)
        
    # Sort suggestions in each group by search_volume descending
    for src in groups:
        groups[src].sort(key=lambda x: x.get("search_volume") or 0, reverse=True)
        
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# AnswerThePublic Keyword Report\n\n")
        f.write(f"- **Query:** `{query}`\n")
        f.write(f"- **Region:** `{region.upper()}`\n")
        f.write(f"- **Language:** `{lang.upper()}`\n")
        f.write(f"- **Total Suggestions:** `{len(suggestions)}`\n\n")
        
        f.write("## Category Breakdown\n\n")
        f.write("| Category | Count |\n")
        f.write("| --- | --- |\n")
        for src in sorted(groups.keys()):
            f.write(f"| {src} | {len(groups[src])} |\n")
        f.write("\n")
        
        # Output tables for each source category
        # Standard source categories: questions, prepositions, comparisons, alphabeticals, related
        for src in sorted(groups.keys()):
            f.write(f"## Category: {src.capitalize()}\n\n")
            f.write("| Suggestion | Search Volume | Cost Per Click ($) |\n")
            f.write("| --- | --- | --- |\n")
            for item in groups[src]:
                vol = item.get("search_volume")
                vol_str = f"{int(vol)}" if vol is not None else "N/A"
                cpc = item.get("cost_per_click")
                cpc_str = f"{cpc:.2f}" if cpc is not None else "N/A"
                # Escape pipe characters in suggestion just in case
                sug_esc = item.get("suggestion", "").replace("|", "\\|")
                f.write(f"| {sug_esc} | {vol_str} | {cpc_str} |\n")
            f.write("\n")
            
    print(f"Saved human-readable markdown report to: {report_file.name}")

def make_request_with_retry(method, url, headers=None, json_data=None, params=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if method == "POST":
                response = requests.post(url, json=json_data, headers=headers, timeout=60)
            else:
                response = requests.get(url, params=params, headers=headers, timeout=60)
                
            # Handle rate limit (429)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                sleep_sec = int(retry_after) if retry_after else 10
                print(f"Rate limited (429). Sleeping for {sleep_sec} seconds before retry...")
                time.sleep(sleep_sec)
                continue
                
            # Handle transient internal server error (500)
            if response.status_code == 500:
                print(f"Server error (500). Retrying in 5 seconds (attempt {attempt + 1}/{max_retries})...")
                time.sleep(5)
                continue
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            
    # Final attempt
    if method == "POST":
        return requests.post(url, json=json_data, headers=headers, timeout=60)
    else:
        return requests.get(url, params=params, headers=headers, timeout=60)

def fetch_from_atp(query, region, lang):
    if not ANSWERTHEPUBLIC_API_KEY:
        print("Error: ANSWERTHEPUBLIC_API_KEY not found in environment variables or .env file.")
        sys.exit(1)
        
    headers = {
        "Authorization": f"Bearer {ANSWERTHEPUBLIC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Create the search
    create_url = "https://api.answerthepublic.com/api/public/v1/searches"
    payload = {
        "search": {
            "keyword": query,
            "language": lang.lower(),
            "region": region.lower(),
            "provider": "gweb"
        }
    }
    
    print(f"Initiating AnswerThePublic search for query: '{query}'...")
    response = make_request_with_retry("POST", create_url, headers=headers, json_data=payload)
    
    if response.status_code == 403:
        # Billing limit or forbidden
        err_msg = "Unknown error"
        try:
            err_msg = response.json().get("error", {}).get("message", response.text)
        except Exception:
            err_msg = response.text
        print(f"\nError 403: Action forbidden. You may have exhausted your monthly credit allowance.")
        print(f"Details from API: {err_msg}")
        sys.exit(1)
        
    if response.status_code not in (200, 201):
        print(f"Failed to create search (HTTP {response.status_code}): {response.text}")
        sys.exit(1)
        
    res_data = response.json().get("data", {})
    parent_search_id = res_data.get("parent_search_id")
    searches = res_data.get("searches", [])
    
    # Find gweb search details
    gweb_search = next((s for s in searches if s.get("provider") == "gweb"), None)
    if not gweb_search:
        print(f"Error: No 'gweb' search found in the creation response: {res_data}")
        sys.exit(1)
        
    child_search_id = gweb_search.get("id")
    initial_status = gweb_search.get("status")
    
    # 2. Poll for completion
    status = initial_status
    poll_url = f"https://api.answerthepublic.com/api/public/v1/searches/{child_search_id}"
    
    start_time = time.time()
    max_poll_time = 300  # 5 minutes
    
    while status in ("loading", "pending"):
        elapsed = int(time.time() - start_time)
        if elapsed > max_poll_time:
            print("\nError: Polling timed out after 5 minutes.")
            sys.exit(1)
            
        print(f"Polling search status... (currently '{status}', elapsed: {elapsed}s)")
        time.sleep(5)
        
        poll_resp = make_request_with_retry("GET", poll_url, headers=headers)
        if poll_resp.status_code != 200:
            print(f"Failed to poll search status (HTTP {poll_resp.status_code}): {poll_resp.text}")
            sys.exit(1)
            
        poll_data = poll_resp.json().get("data", {})
        status = poll_data.get("status")
        
    if status == "failed":
        print("\nError: The keyword search failed on the AnswerThePublic server.")
        sys.exit(1)
        
    print(f"Search completed on server!")
    
    # 3. Retrieve flat report pages
    report_url = f"https://api.answerthepublic.com/api/public/v1/reports/{parent_search_id}"
    suggestions = []
    page = 1
    
    print("Retrieving reports from AnswerThePublic...")
    while True:
        params = {"page": page}
        rep_resp = make_request_with_retry("GET", report_url, headers=headers, params=params)
        
        if rep_resp.status_code != 200:
            print(f"Failed to retrieve report page {page} (HTTP {rep_resp.status_code}): {rep_resp.text}")
            sys.exit(1)
            
        rep_data = rep_resp.json().get("data", {})
        search_engine = rep_data.get("search_engine", {})
        gweb = search_engine.get("gweb", {})
        results = gweb.get("results", {})
        page_data = results.get("data", [])
        page_info = results.get("page_info", {})
        
        suggestions.extend(page_data)
        
        next_page = page_info.get("next_page")
        if next_page:
            page = next_page
        else:
            break
            
    # 4. Construct unified cached response format
    cache_payload = {
        "message": "Report retrieved successfully",
        "data": {
            "search_engine": {
                "gweb": {
                    "id": child_search_id,
                    "completed": True,
                    "results": {
                        "data": suggestions,
                        "page_info": {
                            "page": 1,
                            "next_page": None,
                            "previous_page": None,
                            "per_page": len(suggestions),
                            "total_pages": 1
                        }
                    }
                }
            }
        }
    }
    
    return cache_payload

def print_summary(query, suggestions):
    # Count by source
    groups = {}
    for sug in suggestions:
        src = sug.get("source_name", "unknown")
        groups[src] = groups.get(src, 0) + 1
        
    print(f"\nSuccessfully retrieved search data for query: '{query}'")
    print(f"Total keyword suggestions: {len(suggestions)}")
    print("Breakdown by source:")
    for src, count in sorted(groups.items()):
        print(f"  - {src}: {count}")
        
    # List top questions
    questions = [sug for sug in suggestions if sug.get("source_name") == "questions"]
    # Sort by volume descending, placing items with volume at top
    questions.sort(key=lambda x: x.get("search_volume") or 0, reverse=True)
    
    print(f"\nTop 'Questions' discovered ({len(questions)} total):")
    for q in questions[:15]:
        vol = q.get("search_volume")
        vol_str = f"Volume: {int(vol)}" if vol is not None else "Volume: N/A"
        cpc = q.get("cost_per_click")
        cpc_str = f"CPC: ${cpc:.2f}" if cpc is not None else "CPC: N/A"
        print(f"  - {q.get('suggestion')} ({vol_str}, {cpc_str})")

def main():
    parser = argparse.ArgumentParser(description="AnswerThePublic REST API crawler and local cache manager.")
    parser.add_argument("--query", required=True, help="Target search query (or comma-separated queries, e.g. 'well cost, well repair')")
    parser.add_argument("--region", default="US", help="Target region/country code (default: US)")
    parser.add_argument("--lang", default="EN", help="Target language code (default: EN)")
    
    args = parser.parse_args()
    
    # Split queries by comma to support multi-query batch runs in a single execution
    queries = [q.strip() for q in args.query.split(",") if q.strip()]
    
    new_search_count = 0
    governor_limit = 5
    
    for idx, query in enumerate(queries):
        if len(queries) > 1:
            print(f"\n--- Processing query {idx + 1}/{len(queries)}: '{query}' ---")
            
        cache_file = get_cache_path(query, args.region, args.lang)
        
        # Check local cache first
        if cache_file.exists():
            print(f"Loading search results from local cache: {cache_file.name}")
            with open(cache_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
        else:
            # Enforce credit governor limit for new API fetches
            new_search_count += 1
            if new_search_count >= governor_limit:
                print(f"\n[GOVERNOR] Warning: About to execute new API search #{new_search_count} ('{query}') in this run.")
                print("This will consume credits from the AnswerThePublic account limit (60/month).")
                ans = input("Do you want to proceed? (y/n): ").strip().lower()
                if ans != 'y':
                    print("Skipping remaining searches.")
                    break
            
            # Fetch fresh data
            payload = fetch_from_atp(query, args.region, args.lang)
            
            # Save to local cache
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Saved results to local cache: {cache_file.name}")
            
        # Parse suggestions from payload structure
        data_block = payload.get("data", {})
        search_engine = data_block.get("search_engine", {})
        gweb = search_engine.get("gweb", {})
        results = gweb.get("results", {})
        suggestions = results.get("data", [])
        
        # Write human-readable markdown report
        write_markdown_report(query, args.region, args.lang, suggestions)
        
        # Print summary of results
        print_summary(query, suggestions)

if __name__ == "__main__":
    main()
