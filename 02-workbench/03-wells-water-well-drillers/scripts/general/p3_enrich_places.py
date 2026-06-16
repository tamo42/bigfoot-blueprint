import os
import sys
import json
import time
import sqlite3
import argparse
import requests

# Set path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import p3_utils as utils
import p3_schema as schema

def enrich_state_database(db_path, state_name, max_queries):
    """
    Enriches the SQLite database at db_path using Google Places API.
    """
    # 1. Load API Key
    api_key = utils.load_env_api_key()
    if not api_key:
        print("[-] Error: GOOGLE_PLACES_API_KEY not found in .env at workspace root.")
        sys.exit(1)
        
    # 2. Ensure schema is initialized
    schema.initialize_database(db_path)
    
    # 3. Load Places API Cache
    places_cache_path = utils.get_places_cache_path()
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
            os.makedirs(os.path.dirname(places_cache_path), exist_ok=True)
            with open(places_cache_path, 'w', encoding='utf-8') as f:
                json.dump(places_cache, f, indent=2)
        except Exception as e:
            print(f"[-] Error saving Places cache: {e}")

    # 4. Query DB for rows needing enrichment
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    state_map = {
        "georgia": "GA", "michigan": "MI", "new york": "NY", "new_york": "NY",
        "north carolina": "NC", "north_carolina": "NC", "ohio": "OH",
        "pennsylvania": "PA", "texas": "TX", "virginia": "VA",
        "ga": "GA", "mi": "MI", "ny": "NY", "nc": "NC", "oh": "OH",
        "pa": "PA", "tx": "TX", "va": "VA"
    }
    state_abbrev = state_map.get(state_name.lower(), state_name.upper()) if state_name else None
    
    if state_abbrev:
        c.execute("SELECT id, name, city FROM well_contractors WHERE (google_place_id IS NULL OR google_place_id = '') AND UPPER(state) = ?", (state_abbrev,))
    else:
        c.execute("SELECT id, name, city FROM well_contractors WHERE google_place_id IS NULL OR google_place_id = ''")
    rows = c.fetchall()

    print(f"[*] Found {len(rows)} records in database needing enrichment.")
    
    queries_made = 0
    updated_count = 0
    
    for row in rows:
        row_id, name, city = row
        safe_city = city if city else ""
        cache_key = f"{name.lower()} | {safe_city.lower()}"
        
        res = None
        if cache_key in places_cache:
            res = places_cache[cache_key]
            print(f"[+] Cache hit: {name} in {safe_city}")
        else:
            if queries_made >= max_queries:
                print("[-] Reached safety query limit for this run.")
                break
                
            search_query = f"{name} {safe_city} {state_name}".strip()
            print(f"[*] Querying Places API ({queries_made + 1}/{max_queries}): '{search_query}'...")
            
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
                "reviews_json": None,
                "reviews_detail": []
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
                            res["reviews_detail"] = [
                                {
                                    "text": r.get('text'),
                                    "author_name": r.get('author_name'),
                                    "rating": r.get('rating')
                                }
                                for r in reviews
                            ]
                
                # Save to cache
                places_cache[cache_key] = res
                save_places_cache()
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  [-] Error querying Places API for {name}: {e}")
                continue
                
        # If we have a place_id (from cache or new API call), update SQLite
        if res and res.get("place_id"):
            r1_text = r1_author = r1_rating = None
            r2_text = r2_author = r2_rating = None
            r3_text = r3_author = r3_rating = None
            
            reviews_detail = res.get("reviews_detail", [])
            if reviews_detail:
                if len(reviews_detail) > 0:
                    r1_text = reviews_detail[0].get('text')
                    r1_author = reviews_detail[0].get('author_name')
                    r1_rating = reviews_detail[0].get('rating')
                if len(reviews_detail) > 1:
                    r2_text = reviews_detail[1].get('text')
                    r2_author = reviews_detail[1].get('author_name')
                    r2_rating = reviews_detail[1].get('rating')
                if len(reviews_detail) > 2:
                    r3_text = reviews_detail[2].get('text')
                    r3_author = reviews_detail[2].get('author_name')
                    r3_rating = reviews_detail[2].get('rating')
            else:
                # Fallback to standard reviews_json if old cache
                try:
                    if res.get("reviews_json"):
                        txt_list = json.loads(res.get("reviews_json"))
                        if len(txt_list) > 0: r1_text = txt_list[0]
                        if len(txt_list) > 1: r2_text = txt_list[1]
                        if len(txt_list) > 2: r3_text = txt_list[2]
                except Exception:
                    pass
                    
            c.execute('''
                UPDATE well_contractors
                SET google_place_id = ?,
                    website_url = ?,
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
                res.get("place_id"),
                res.get("website_url"),
                res.get("rating") if res.get("rating") else 0,
                res.get("reviews_count") if res.get("reviews_count") else 0,
                res.get("latitude"),
                res.get("longitude"),
                res.get("reviews_json"),
                r1_text, r1_author, r1_rating,
                r2_text, r2_author, r2_rating,
                r3_text, r3_author, r3_rating,
                row_id
            ))
            updated_count += 1
            
    conn.commit()
    conn.close()
    
    approx_cost = queries_made * (0.017 + 0.025)
    print(f"\n[+] Enrichment run completed for {state_name}.")
    print(f"    - Updated {updated_count} records in SQLite.")
    print(f"    - Approximate Google Places API cost: ${approx_cost:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Enrich state SQLite database with Google Places details.")
    parser.add_argument("--state", type=str, required=True, help="State name or state database prefix (e.g. georgia, ohio, texas).")
    parser.add_argument("--db", type=str, help="Direct path to SQLite database. If omitted, resolved automatically via --state.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of Find Place API queries to perform (default 100).")
    
    args = parser.parse_args()
    
    state = args.state
    max_queries = args.limit
    
    if args.db:
        db_path = os.path.abspath(args.db)
    else:
        db_path = utils.get_unified_db_path()
        
    print(f"[*] Target State: {state.title()}")
    print(f"[*] Target Database Path: {db_path}")
    print(f"[*] Safety Query Limit: {max_queries}")
    
    if not os.path.exists(db_path):
        print(f"[-] Error: SQLite database not found at: {db_path}")
        sys.exit(1)
        
    enrich_state_database(db_path, state.title(), max_queries)

if __name__ == "__main__":
    main()
