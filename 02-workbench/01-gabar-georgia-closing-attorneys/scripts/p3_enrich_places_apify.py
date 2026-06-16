import os
import sys
import json
import time
import sqlite3
import argparse
import requests

def load_apify_token():
    # Look for .env at project root
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        env_path = os.path.join(current, ".env")
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('APIFY_API_TOKEN='):
                        return line.split('=', 1)[1].strip()
            return None
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None

def main():
    parser = argparse.ArgumentParser(description="Enrich database using Apify Google Maps Scraper actor.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of listings to enrich in this batch.")
    args = parser.parse_args()
    
    token = load_apify_token()
    if not token:
        print("[-] Error: APIFY_API_TOKEN not found in .env at workspace root.")
        sys.exit(1)
        
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "directory.sqlite"))
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, first_name, last_name, firm_name, city 
        FROM attorneys 
        WHERE google_place_id IS NULL OR google_place_id = ''
    """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print(f"[+] All records in database are already enriched.")
        return
        
    rows = rows[:args.limit]
    print(f"[*] Batching {len(rows)} records for Apify enrichment...")
    
    query_to_id = {}
    search_queries = []
    
    for row in rows:
        row_id, first_name, last_name, firm_name, city = row
        name = f"{first_name} {last_name}"
        firm = firm_name if firm_name and str(firm_name).strip() and str(firm_name).lower() not in ['none', 'n/a'] else ""
        
        search_query = f"{firm} {name} closing attorney {city} GA".strip()
        search_queries.append(search_query)
        query_to_id[search_query.lower()] = row_id

    print("[*] Launching compass/crawler-google-places run...")
    actor_id = "compass~crawler-google-places"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={token}"
    
    payload = {
        "searchStringsArray": search_queries,
        "maxResultsPerQuery": 1,
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
    
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"
    max_wait_seconds = 600
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
        
    print("[*] Scrape complete. Fetching dataset items...")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"
    
    try:
        items = requests.get(dataset_url, timeout=30).json()
        print(f"[+] Retrieved {len(items)} items from Apify dataset.")
    except Exception as e:
        print(f"[-] Failed to download dataset items: {e}")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    updated_count = 0
    
    for item in items:
        search_query = item.get("searchString", "")
        if not search_query:
            search_query = f"{item.get('title')}, {item.get('city')}, GA"
            
        row_id = query_to_id.get(search_query.lower())
        if not row_id:
            title = item.get("title", "")
            for q_str, r_id in query_to_id.items():
                if title.lower() in q_str:
                    row_id = r_id
                    break
                    
        if not row_id:
            continue
            
        place_id = item.get("placeId")
        website = item.get("website")
        rating = item.get("totalScore") or item.get("stars") or 0.0
        reviews_count = item.get("reviewsCount") or 0
        
        lat = lng = None
        location_obj = item.get("location")
        if location_obj and isinstance(location_obj, dict):
            lat = location_obj.get("lat")
            lng = location_obj.get("lng")
            
        raw_reviews = item.get("reviews", [])
        
        rev_data = []
        for i in range(5):
            if i < len(raw_reviews):
                rev = raw_reviews[i]
                author = rev.get("name") or rev.get("authorName")
                r_rating = rev.get("stars") or rev.get("rating")
                text = rev.get("text", "")
                if text: text = text[:300]
                rev_data.append((author, r_rating, text))
            else:
                rev_data.append((None, None, None))
                
        c.execute('''
            UPDATE attorneys
            SET google_place_id = ?,
                website_url = ?,
                google_rating = ?,
                google_review_count = ?,
                latitude = ?,
                longitude = ?,
                review_1_author = ?, review_1_rating = ?, review_1_text = ?,
                review_2_author = ?, review_2_rating = ?, review_2_text = ?,
                review_3_author = ?, review_3_rating = ?, review_3_text = ?,
                review_4_author = ?, review_4_rating = ?, review_4_text = ?,
                review_5_author = ?, review_5_rating = ?, review_5_text = ?
            WHERE id = ?
        ''', (
            place_id, website, rating, reviews_count, lat, lng,
            rev_data[0][0], rev_data[0][1], rev_data[0][2],
            rev_data[1][0], rev_data[1][1], rev_data[1][2],
            rev_data[2][0], rev_data[2][1], rev_data[2][2],
            rev_data[3][0], rev_data[3][1], rev_data[3][2],
            rev_data[4][0], rev_data[4][1], rev_data[4][2],
            row_id
        ))
        updated_count += 1
        
    conn.commit()
    conn.close()
    
    print(f"[+] Enrichment finished. Successfully updated {updated_count} rows in database.")

if __name__ == "__main__":
    main()
