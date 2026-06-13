import os
import sys
import json
import sqlite3
import argparse
import time
import requests
from pathlib import Path

# Load dotenv manually to support workspace-level .env files
def load_dotenv():
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

PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

def fetch_place_details(place_id):
    if not PLACES_API_KEY:
        print("Error: GOOGLE_PLACES_API_KEY not found in environment variables or .env file.")
        return None
        
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,opening_hours,reviews",
        "key": PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("result", {})
    except Exception as e:
        print(f"Error fetching place details: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Enrich database with Google Places Details.")
    parser.add_argument("--limit", type=int, default=5, help="Limit the number of records to enrich (default: 5)")
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    db_file = script_dir.parent / "data" / "directory.sqlite"
    
    if not db_file.exists():
        print(f"Error: Database file '{db_file.name}' not found. Run import-seed.py first.")
        return
        
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Query records where website_url and phone are null (unenriched)
    # Check if reviews_json is default empty list to determine if details were fetched
    c.execute("""
        SELECT id, name, place_id 
        FROM installers_haulers 
        WHERE (phone IS NULL OR website_url IS NULL) AND reviews_json = '[]'
        LIMIT ?
    """, (args.limit,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending unenriched records found in database.")
        conn.close()
        return
        
    print(f"Enriching {len(records)} records from Google Places Details API (Limit: {args.limit})...")
    
    for i, row in enumerate(records):
        record_id = row["id"]
        name = row["name"]
        place_id = row["place_id"]
        
        print(f"[{i+1}/{len(records)}] Processing details for: '{name}'...")
        
        details = fetch_place_details(place_id)
        if details:
            phone = details.get("formatted_phone_number")
            website = details.get("website")
            
            # Extract review text snippets
            reviews = [r.get("text", "") for r in details.get("reviews", []) if r.get("text")]
            reviews_json = json.dumps(reviews[:3]) # Limit to top 3 snippets
            
            # Log results
            print(f"  - Phone: {phone}")
            print(f"  - Website: {website}")
            print(f"  - Reviews Snippets: {len(reviews)} found.")
            
            c.execute("""
                UPDATE installers_haulers
                SET phone = ?,
                    website_url = ?,
                    reviews_json = ?
                WHERE id = ?
            """, (phone, website, reviews_json, record_id))
            
            conn.commit()
            print(f"  [+] Committed ID {record_id} to database.")
        else:
            print(f"  [-] Failed to fetch details for Place ID: {place_id}")
            
        # Politeness delay
        time.sleep(0.7)
        
    conn.close()
    print("\nEnrichment Batch Complete.")

if __name__ == "__main__":
    main()
