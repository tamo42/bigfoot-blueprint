import os
import sys
import sqlite3
import json
import time
import urllib.request
import urllib.parse
import argparse

def get_project_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(current, ".env")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            # Fallback to current script directory's grandparent if no .env found
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        current = parent

def load_api_key():
    root = get_project_root()
    env_path = os.path.join(root, ".env")
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                if key.strip() == "GOOGLE_PLACES_API_KEY":
                    return val.strip().strip('"').strip("'")
    return None

def setup_schema(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(attorneys)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    new_columns = [
        ("google_place_id", "TEXT"),
        ("google_rating", "REAL"),
        ("google_review_count", "INTEGER"),
        ("review_1_author", "TEXT"),
        ("review_1_rating", "INTEGER"),
        ("review_1_text", "TEXT"),
        ("review_2_author", "TEXT"),
        ("review_2_rating", "INTEGER"),
        ("review_2_text", "TEXT"),
        ("review_3_author", "TEXT"),
        ("review_3_rating", "INTEGER"),
        ("review_3_text", "TEXT"),
        ("review_4_author", "TEXT"),
        ("review_4_rating", "INTEGER"),
        ("review_4_text", "TEXT"),
        ("review_5_author", "TEXT"),
        ("review_5_rating", "INTEGER"),
        ("review_5_text", "TEXT")
    ]
    
    altered = False
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            print(f"Adding column {col_name} ({col_type}) to attorneys table...")
            cursor.execute(f"ALTER TABLE attorneys ADD COLUMN {col_name} {col_type}")
            altered = True
    
    if altered:
        conn.commit()
        print("Database schema updated successfully with Google Places columns.")
    else:
        print("Database schema already includes all Google Places columns.")

def search_places(query, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query)}&key={api_key}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    for attempt in range(1, 4):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                status = res_json.get('status', 'UNKNOWN')
                
                if status == 'OK':
                    results = res_json.get('results', [])
                    if results:
                        return results[0].get('place_id'), None
                elif status == 'ZERO_RESULTS':
                    return None, 'ZERO_RESULTS'
                elif status == 'OVER_QUERY_LIMIT':
                    if attempt < 3:
                        print(f"  Received OVER_QUERY_LIMIT. Retrying attempt {attempt+1} in 3 seconds...")
                        time.sleep(3)
                        continue
                    return None, 'OVER_QUERY_LIMIT'
                elif status == 'REQUEST_DENIED':
                    err_msg = res_json.get('error_message', '')
                    if "referer restrictions" in err_msg and attempt < 3:
                        print(f"  WARNING: Google API reported referer restriction (propagation lag). Retrying search attempt {attempt+1} in 5 seconds...")
                        time.sleep(5)
                        continue
                    return None, f"REQUEST_DENIED: {err_msg}"
                else:
                    return None, status
        except Exception as e:
            if attempt < 3:
                time.sleep(2)
                continue
            return None, str(e)
    return None, 'NO_RESULTS'

def get_place_details(place_id, api_key):
    fields = "website,formatted_phone_number,geometry/location,rating,user_ratings_total,reviews"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={api_key}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    for attempt in range(1, 4):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                status = res_json.get('status', 'UNKNOWN')
                
                if status == 'OK':
                    return res_json.get('result', {}), None
                elif status == 'OVER_QUERY_LIMIT':
                    if attempt < 3:
                        print(f"  Received OVER_QUERY_LIMIT. Retrying details attempt {attempt+1} in 3 seconds...")
                        time.sleep(3)
                        continue
                    return None, 'OVER_QUERY_LIMIT'
                elif status == 'REQUEST_DENIED':
                    err_msg = res_json.get('error_message', '')
                    if "referer restrictions" in err_msg and attempt < 3:
                        print(f"  WARNING: Google API reported referer restriction (propagation lag). Retrying details attempt {attempt+1} in 5 seconds...")
                        time.sleep(5)
                        continue
                    return None, f"REQUEST_DENIED: {err_msg}"
                else:
                    return None, status
        except Exception as e:
            if attempt < 3:
                time.sleep(2)
                continue
            return None, str(e)
    return None, 'NO_DETAILS_ERROR'

def main():
    parser = argparse.ArgumentParser(description="Georgia Closing Attorneys Google Places Enrichment Script")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of records to enrich (for testing)")
    args = parser.parse_args()
    
    print("=========================================================")
    print("Georgia Closing Attorneys - Google Places Ingestion")
    print("=========================================================")
    
    api_key = load_api_key()
    if not api_key:
        print("Error: GOOGLE_PLACES_API_KEY not found in .env file. Exiting.")
        sys.exit(1)
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(current_dir), "data", "directory.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # 1. Update schema with Google Places columns if necessary
    setup_schema(conn)
    
    cursor = conn.cursor()
    
    # 2. Query un-enriched records
    cursor.execute("""
        SELECT id, first_name, last_name, firm_name, city 
        FROM attorneys 
        WHERE google_place_id IS NULL
    """)
    records = cursor.fetchall()
    total_records = len(records)
    print(f"Found {total_records} un-enriched records in the database.")
    
    if total_records == 0:
        print("All records are already enriched or marked. Exiting.")
        conn.close()
        return
        
    # Apply limit if set
    if args.limit is not None:
        records = records[:args.limit]
        print(f"Limiting execution to {len(records)} records for this run.")
        
    success_count = 0
    not_found_count = 0
    error_count = 0
    
    # 3. Process records
    for idx, (rec_id, first_name, last_name, firm_name, city) in enumerate(records):
        try:
            print(f"\n[{idx+1}/{len(records)}] Processing ID {rec_id}: {first_name} {last_name} (Firm: {firm_name}) in {city}...")
            
            # Build query sequence:
            queries = []
            if firm_name and firm_name.strip() and firm_name.strip().lower() not in ["", "none", "n/a"]:
                queries.append(f"{firm_name.strip()} real estate attorney {city} GA")
            
            queries.append(f"{first_name} {last_name} closing attorney {city} GA")
            queries.append(f"{first_name} {last_name} real estate attorney {city} GA")
            queries.append(f"{first_name} {last_name} lawyer {city} GA")
            
            place_id = None
            match_query = None
            api_error = None
            
            for q in queries:
                print(f"  Searching: '{q}'...")
                pid, err = search_places(q, api_key)
                if err == 'OVER_QUERY_LIMIT':
                    print("  WARNING: Over Google API query limit. Waiting 2 seconds before retrying...")
                    time.sleep(2.0)
                    pid, err = search_places(q, api_key)
                    
                if pid:
                    place_id = pid
                    match_query = q
                    print(f"  Found Place ID: {place_id}")
                    break
                elif err and "REQUEST_DENIED" in err:
                    print(f"  CRITICAL API ERROR: {err}")
                    api_error = err
                    break
                else:
                    if err:
                        print(f"  No match or error: {err}")
                        
            if api_error and "REQUEST_DENIED" in api_error:
                print("\nStopping run due to API credentials denial.")
                break
                
            if not place_id:
                # Mark as not found to avoid re-searching in the future
                print("  Result: No Google Place match found. Marking as 'NOT_FOUND'.")
                cursor.execute("UPDATE attorneys SET google_place_id = 'NOT_FOUND' WHERE id = ?", (rec_id,))
                conn.commit()
                not_found_count += 1
                time.sleep(0.5)
                continue
                
            # Call details endpoint
            print(f"  Fetching details for Place ID {place_id}...")
            details, err = get_place_details(place_id, api_key)
            if err == 'OVER_QUERY_LIMIT':
                print("  WARNING: Over Google API query limit. Waiting 2 seconds before retrying...")
                time.sleep(2.0)
                details, err = get_place_details(place_id, api_key)
                
            if not details:
                print(f"  Error fetching details: {err or 'Unknown Error'}. Skipping record.")
                error_count += 1
                time.sleep(0.5)
                continue
                
            # Parse details
            website = details.get('website')
            
            # Latitude and longitude
            geometry = details.get('geometry', {})
            location = geometry.get('location', {})
            lat = location.get('lat')
            lng = location.get('lng')
            
            rating = details.get('rating')
            review_count = details.get('user_ratings_total')
            
            # Parse up to 5 reviews
            reviews = details.get('reviews', [])
            rev_data = []
            for i in range(5):
                if i < len(reviews):
                    rev = reviews[i]
                    author = rev.get('author_name')
                    rev_rating = rev.get('rating')
                    text = rev.get('text', '')
                    if text:
                        text = text[:300] # Truncate to 300 chars
                    rev_data.append((author, rev_rating, text))
                else:
                    rev_data.append((None, None, None))
                    
            # Update record in DB
            cursor.execute("""
                UPDATE attorneys SET
                    google_place_id = ?,
                    google_rating = ?,
                    google_review_count = ?,
                    latitude = ?,
                    longitude = ?,
                    website_url = ?,
                    review_1_author = ?, review_1_rating = ?, review_1_text = ?,
                    review_2_author = ?, review_2_rating = ?, review_2_text = ?,
                    review_3_author = ?, review_3_rating = ?, review_3_text = ?,
                    review_4_author = ?, review_4_rating = ?, review_4_text = ?,
                    review_5_author = ?, review_5_rating = ?, review_5_text = ?
                WHERE id = ?
            """, (
                place_id, rating, review_count, lat, lng, website,
                rev_data[0][0], rev_data[0][1], rev_data[0][2],
                rev_data[1][0], rev_data[1][1], rev_data[1][2],
                rev_data[2][0], rev_data[2][1], rev_data[2][2],
                rev_data[3][0], rev_data[3][1], rev_data[3][2],
                rev_data[4][0], rev_data[4][1], rev_data[4][2],
                rec_id
            ))
            
            conn.commit()
            print(f"  Successfully saved details: Rating: {rating}, Reviews: {review_count}, Lat/Lng: ({lat}, {lng}), Website: {website}")
            success_count += 1
        except Exception as e:
            print(f"  ERROR processing ID {rec_id}: {e}")
            try:
                conn.rollback()
            except sqlite3.Error:
                pass
            error_count += 1
        
        # Polite 0.5s rate limit sleep
        time.sleep(0.5)
        
    conn.close()
    
    print("\n=========================================================")
    print("Enrichment Ingestion Summary")
    print("=========================================================")
    print(f"Total processed:  {success_count + not_found_count + error_count}")
    print(f"Successfully met: {success_count}")
    print(f"Marked not found: {not_found_count}")
    print(f"Errors incurred:  {error_count}")
    print("=========================================================")

if __name__ == "__main__":
    main()
