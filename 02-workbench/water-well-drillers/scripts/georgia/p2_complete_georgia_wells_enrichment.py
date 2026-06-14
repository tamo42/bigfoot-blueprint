import os
import re
import json
import sqlite3
import time
import requests
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

# Load API Key
api_key = utils.load_env_api_key()
if not api_key:
    print("[-] Error: GOOGLE_PLACES_API_KEY not found in .env")
    exit(1)

# Dynamic paths
db_path = utils.get_db_path("georgia")
places_cache_path = utils.get_places_cache_path()

# Load Places API Cache
places_cache = {}
if os.path.exists(places_cache_path):
    try:
        with open(places_cache_path, 'r', encoding='utf-8') as f:
            places_cache = json.load(f)
        print(f"[+] Loaded {len(places_cache)} cached Places API responses.")
    except Exception as e:
        print(f"[-] Error loading Places cache: {e}")

def save_places_cache():
    try:
        with open(places_cache_path, 'w', encoding='utf-8') as f:
            json.dump(places_cache, f, indent=2)
    except Exception as e:
        print(f"[-] Error saving Places cache: {e}")

def main():
    # Ensure schema is correct
    schema.initialize_database(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get rows missing google_place_id
    c.execute("SELECT id, name, city FROM installers_haulers WHERE google_place_id IS NULL OR google_place_id = ''")
    rows = c.fetchall()
    print(f"[*] Found {len(rows)} records in database needing enrichment.")

    queries_made = 0
    updated_count = 0

    for row in rows:
        row_id, name, city = row
        cache_key = f"{name.lower()} | {city.lower()}"
        
        res = None
        if cache_key in places_cache:
            res = places_cache[cache_key]
            print(f"[+] Cache hit for: {name} in {city}")
        else:
            # Respect budget: up to 150 queries in this run
            if queries_made >= 150:
                print("[-] Reached safety query limit for this run.")
                break
                
            search_query = f"{name} {city} Georgia"
            print(f"[*] Querying Places API: '{search_query}'...")
            
            find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            find_params = {
                'input': search_query,
                'inputtype': 'textquery',
                'fields': 'place_id',
                'key': api_key
            }
            
            res = {
                "place_id": None,
                "website_url": None,
                "latitude": None,
                "longitude": None,
                "rating": None,
                "reviews_count": None,
                "reviews_json": None
            }
            
            try:
                find_res = requests.get(find_url, params=find_params, timeout=10).json()
                queries_made += 1
                
                if find_res.get('status') == 'OK' and len(find_res.get('candidates', [])) > 0:
                    place_id = find_res['candidates'][0]['place_id']
                    res["place_id"] = place_id
                    
                    # Place Details
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        'place_id': place_id,
                        'fields': 'website,geometry,rating,user_ratings_total,reviews',
                        'key': api_key
                    }
                    det_res = requests.get(details_url, params=details_params, timeout=10).json()
                    queries_made += 1
                    
                    if det_res.get('status') == 'OK':
                        result = det_res.get('result', {})
                        res["website_url"] = result.get('website')
                        res["rating"] = result.get('rating')
                        res["reviews_count"] = result.get('user_ratings_total')
                        
                        if result.get('geometry') and result['geometry'].get('location'):
                            res["latitude"] = result['geometry']['location'].get('lat')
                            res["longitude"] = result['geometry']['location'].get('lng')
                            
                        reviews = result.get('reviews', [])
                        if reviews:
                            res["reviews_json"] = json.dumps([r.get('text') for r in reviews if r.get('text')])
                
                # Save to cache
                places_cache[cache_key] = res
                save_places_cache()
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  [-] Error querying Places API for {name}: {e}")
                continue

        if res and res.get("place_id"):
            # Update record in DB
            c.execute('''
                UPDATE installers_haulers
                SET google_place_id = ?,
                    website_url = ?,
                    google_rating = ?,
                    google_review_count = ?,
                    manual_lat = ?,
                    manual_lng = ?,
                    reviews_json = ?
                WHERE id = ?
            ''', (
                res.get("place_id"),
                res.get("website_url"),
                res.get("rating") if res.get("rating") else 0,
                res.get("reviews_count") if res.get("reviews_count") else 0,
                res.get("latitude"),
                res.get("longitude"),
                res.get("reviews_json"),
                row_id
            ))
            updated_count += 1

    conn.commit()
    print(f"[+] Completed API enrichment. Updated {updated_count} records in SQLite.")
    print(f"[+] Total API queries made in this run: {queries_made}")
    
    # Post-processing: extract reviews_json and populate review_1_text, review_2_text, review_3_text
    print("[*] Post-processing: Populating individual review text columns...")
    c.execute("SELECT id, reviews_json FROM installers_haulers WHERE reviews_json IS NOT NULL")
    all_reviews = c.fetchall()
    reviews_processed = 0

    for r_id, rev_json in all_reviews:
        if not rev_json:
            continue
        try:
            revs = json.loads(rev_json)
            if not isinstance(revs, list) or len(revs) == 0:
                continue
                
            r1 = revs[0] if len(revs) > 0 else None
            r2 = revs[1] if len(revs) > 1 else None
            r3 = revs[2] if len(revs) > 2 else None
            
            c.execute('''
                UPDATE installers_haulers
                SET review_1_text = ?,
                    review_2_text = ?,
                    review_3_text = ?
                WHERE id = ?
            ''', (r1, r2, r3, r_id))
            reviews_processed += 1
        except Exception as e:
            print(f"  [-] Error parsing reviews JSON for record {r_id}: {e}")

    conn.commit()
    conn.close()
    print(f"[+] Done. Populated review texts for {reviews_processed} records.")

if __name__ == "__main__":
    main()
