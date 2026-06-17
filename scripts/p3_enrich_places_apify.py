import os
import sys
import json
import time
import sqlite3
import argparse
import requests

# Set path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(script_dir)

def load_apify_token():
    """
    Finds and loads the APIFY_API_TOKEN from the .env file at the workspace root.
    """
    env_path = os.path.join(workspace_root, ".env")
    if not os.path.exists(env_path):
        return None
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('APIFY_API_TOKEN='):
                return line.split('=', 1)[1].strip()
    return None

def enrich_state_apify(db_path, state_name, limit):
    """
    Enriches the SQLite database at db_path by calling the Apify Google Maps Scraper actor.
    """
    # 1. Load Apify Token
    token = load_apify_token()
    if not token:
        print("[-] Error: APIFY_API_TOKEN not found in .env at workspace root.")
        sys.exit(1)
        
    # 2. Query DB for rows needing enrichment
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Map state name to abbreviation if needed
    state_abbrev = None
    if state_name and state_name.lower() != 'all':
        state_map = {
            "georgia": "GA", "michigan": "MI", "new york": "NY", "new_york": "NY",
            "north carolina": "NC", "north_carolina": "NC", "ohio": "OH",
            "pennsylvania": "PA", "texas": "TX", "virginia": "VA",
            "ga": "GA", "mi": "MI", "ny": "NY", "nc": "NC", "oh": "OH",
            "pa": "PA", "tx": "TX", "va": "VA"
        }
        state_abbrev = state_map.get(state_name.lower(), state_name.upper())
        
    if state_abbrev:
        c.execute("SELECT id, name, city, state FROM well_contractors WHERE (google_place_id IS NULL OR google_place_id = '' OR phone_number IS NULL OR phone_number = '') AND UPPER(state) = ?", (state_abbrev,))
    else:
        c.execute("SELECT id, name, city, state FROM well_contractors WHERE (google_place_id IS NULL OR google_place_id = '' OR phone_number IS NULL OR phone_number = '')")
        
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print(f"[+] All records in database are already enriched.")
        return
        
    # Apply limit
    rows = rows[:limit]
    print(f"[*] Batching {len(rows)} records for Apify enrichment...")
    
    # Map search queries to DB IDs
    query_to_id = {}
    search_queries = []
    
    for row in rows:
        row_id, name, city, state = row
        safe_city = city if city else ""
        safe_state = state if state else (state_name if state_name else "")
        # Create unique query string
        search_query = f"{name}, {safe_city}, {safe_state}".strip()
        search_queries.append(search_query)
        
        import re
        clean_key = re.sub(r'\s+', ' ', search_query).lower()
        query_to_id[clean_key] = row_id

    # 3. Call Apify API to run actor
    print("[*] Launching compass/crawler-google-places run...")
    actor_id = "compass~crawler-google-places"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={token}"
    
    payload = {
        "searchStringsArray": search_queries,
        "maxCrawledPlacesPerSearch": 1,
        "maxCrawledPlaces": len(search_queries),
        "scrapeResponseHeaders": False,
        "scrapeReviews": True,
        "maxReviews": 5,
        "languageCode": "en",
        "onlyDataFromSearchPage": False,
        "multiplier": 1
    }
    
    try:
        run_res = requests.post(run_url, json=payload, timeout=30)
        run_res.raise_for_status()
        run_data = run_res.json()
    except Exception as e:
        print(f"[-] Failed to start Apify actor run: {e}")
        return
        
    run_id = run_data["data"]["id"]
    dataset_id = run_data["data"]["defaultDatasetId"]
    print(f"[+] Run started successfully. Run ID: {run_id} | Dataset ID: {dataset_id}")
    
    # 4. Poll actor status until complete
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"
    max_wait_seconds = 600 # 10 minutes timeout
    wait_interval = 15
    elapsed = 0
    
    print("[*] Waiting for Apify scraper to finish (polling every 15s)...")
    while elapsed < max_wait_seconds:
        time.sleep(wait_interval)
        elapsed += wait_interval
        
        try:
            status_res = requests.get(status_url, timeout=20).json()
            status = status_res["data"]["status"]
            print(f"    - Elapsed: {elapsed}s | Status: {status}")
            
            if status == "SUCCEEDED":
                break
            elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                print(f"[-] Apify actor run ended with status: {status}")
                return
        except Exception as e:
            print(f"    - Warning: Failed to query status: {e}")
            
    if elapsed >= max_wait_seconds:
        print("[-] Apify actor run timed out on local polling limit.")
        return
        
    # 5. Download dataset results
    print("[*] Scrape complete. Fetching dataset items...")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"
    
    try:
        items = requests.get(dataset_url, timeout=30).json()
        print(f"[+] Retrieved {len(items)} items from Apify dataset.")
        
        # Save raw extraction payload to cache for data engineering best practices
        cache_dir = os.path.join(workspace_root, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        raw_cache_path = os.path.join(cache_dir, f"apify_raw_dataset_{dataset_id}.json")
        with open(raw_cache_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4)
        print(f"[*] Saved raw Apify dataset payload to {raw_cache_path}")
        
    except Exception as e:
        print(f"[-] Failed to download dataset items: {e}")
        return
        
    # 6. Parse and update SQLite
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    updated_count = 0
    updated_ids = set()
    import re
    
    for item in items:
        # Match by search query returned in the dataset
        search_query = item.get("searchString", "")
        if not search_query:
            # Fallback matching by name
            search_query = f"{item.get('title')}, {item.get('city')}, {state_name}"
            
        clean_search = re.sub(r'\s+', ' ', search_query).lower()
        row_id = query_to_id.get(clean_search)
        
        if not row_id:
            # Try matching title directly
            title = item.get("title", "")
            for q_str, r_id in query_to_id.items():
                if title.lower() in q_str:
                    row_id = r_id
                    break
                    
        if not row_id or row_id in updated_ids:
            continue
            
        updated_ids.add(row_id)
            
        # Extract fields
        place_id = item.get("placeId")
        website = item.get("website")
        phone = item.get("phoneUnformatted") or item.get("phone")
        rating = item.get("totalScore") or item.get("stars") or 0.0
        reviews_count = item.get("reviewsCount") or 0
        
        lat = lng = None
        location_obj = item.get("location")
        if location_obj and isinstance(location_obj, dict):
            lat = location_obj.get("lat")
            lng = location_obj.get("lng")
            
        # Reviews parsing (max 3 reviews)
        raw_reviews = item.get("reviews", [])
        reviews_json = json.dumps(raw_reviews)
        
        r1_text = r1_author = r1_rating = None
        r2_text = r2_author = r2_rating = None
        r3_text = r3_author = r3_rating = None
        
        if len(raw_reviews) > 0:
            r1_text = raw_reviews[0].get("text")
            r1_author = raw_reviews[0].get("name") or raw_reviews[0].get("authorName")
            r1_rating = raw_reviews[0].get("stars") or raw_reviews[0].get("rating")
        if len(raw_reviews) > 1:
            r2_text = raw_reviews[1].get("text")
            r2_author = raw_reviews[1].get("name") or raw_reviews[1].get("authorName")
            r2_rating = raw_reviews[1].get("stars") or raw_reviews[1].get("rating")
        if len(raw_reviews) > 2:
            r3_text = raw_reviews[2].get("text")
            r3_author = raw_reviews[2].get("name") or raw_reviews[2].get("authorName")
            r3_rating = raw_reviews[2].get("stars") or raw_reviews[2].get("rating")
            
        c.execute('''
            UPDATE well_contractors
            SET google_place_id = ?,
                website_url = ?,
                phone_number = ?,
                google_rating = ?,
                google_review_count = ?,
                manual_lat = ?,
                manual_lng = ?,
                reviews_json = ?,
                review_1_text = ?,
                review_1_author = ?,
                review_1_rating = ?,
                review_2_text = ?,
                review_2_author = ?,
                review_2_rating = ?,
                review_3_text = ?,
                review_3_author = ?,
                review_3_rating = ?
            WHERE id = ?
        ''', (
            place_id,
            website,
            phone,
            rating,
            reviews_count,
            lat,
            lng,
            reviews_json,
            r1_text, r1_author, r1_rating,
            r2_text, r2_author, r2_rating,
            r3_text, r3_author, r3_rating,
            row_id
        ))
        updated_count += 1
        
    conn.commit()
    conn.close()
    
    print(f"[+] Enrichment finished. Successfully updated {updated_count} rows in database.")

def main():
    parser = argparse.ArgumentParser(description="Enrich database using Apify Google Maps Scraper actor.")
    parser.add_argument("--state", type=str, default="all", help="State to enrich (e.g. georgia, texas, or 'all').")
    parser.add_argument("--db", type=str, help="Direct path to SQLite database. If omitted, uses unified database.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of listings to enrich in this batch.")
    
    args = parser.parse_args()
    
    state = args.state
    limit = args.limit
    
    if args.db:
        db_path = os.path.abspath(args.db)
    else:
        print("[-] Error: --db argument is required.")
        sys.exit(1)
        
    if not os.path.exists(db_path):
        print(f"[-] Error: Database not found at: {db_path}")
        sys.exit(1)
        
    print(f"[*] Target State: {state.title()}")
    print(f"[*] Database Path: {db_path}")
    print(f"[*] Batch Limit: {limit}")
    
    enrich_state_apify(db_path, state, limit)

if __name__ == "__main__":
    main()
