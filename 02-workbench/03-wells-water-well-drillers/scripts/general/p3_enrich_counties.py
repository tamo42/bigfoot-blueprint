import os
import sys
import csv
import urllib.request
import sqlite3
import argparse

def get_workspace_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))

def download_cities_db(cache_dir):
    csv_path = os.path.join(cache_dir, "us_cities.csv")
    if not os.path.exists(csv_path):
        print("[*] Downloading US Cities Database...")
        os.makedirs(cache_dir, exist_ok=True)
        url = 'https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv'
        urllib.request.urlretrieve(url, csv_path)
        print("[+] Download complete.")
    return csv_path

def load_city_county_lookup(csv_path):
    lookup = {}
    print("[*] Building City -> County lookup table...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state_code = row['STATE_CODE'].strip().upper()
            state_name = row['STATE_NAME'].strip().upper()
            city = row['CITY'].strip().upper()
            county = row['COUNTY'].strip()
            
            # Allow lookup by both state code and state full name
            lookup[(state_code, city)] = county
            lookup[(state_name, city)] = county
    print(f"[+] Loaded {len(lookup)//2} unique city mappings.")
    return lookup

def enrich_counties(db_path, limit=None):
    if not os.path.exists(db_path):
        print(f"[-] Database not found: {db_path}")
        return

    workspace = get_workspace_root()
    cache_dir = os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "cache", "us_cities")
    
    csv_path = download_cities_db(cache_dir)
    lookup = load_city_county_lookup(csv_path)

    print(f"[*] Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT id, state, city FROM well_contractors WHERE county IS NULL OR county = ''"
    if limit:
        query += f" LIMIT {limit}"
        
    c.execute(query)
    rows = c.fetchall()

    if not rows:
        print("[+] No records found lacking a county.")
        conn.close()
        return

    print(f"[*] Attempting to backfill {len(rows)} orphaned records...")

    updates = []
    enriched = 0

    for row in rows:
        row_id = row['id']
        state = row['state']
        city = row['city']
        
        if not state or not city:
            continue
            
        state_clean = state.strip().upper()
        city_clean = city.strip().upper()
        
        county = lookup.get((state_clean, city_clean))
        
        if county:
            updates.append((county, row_id))
            enriched += 1

    if updates:
        print(f"\n[+] Applying {len(updates)} database updates...")
        c.executemany("UPDATE well_contractors SET county = ? WHERE id = ?", updates)
        conn.commit()
    
    print(f"[+] Successfully backfilled {enriched} records with their primary county.")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill missing primary counties using a City-to-County lookup.")
    parser.add_argument("--db", default=None, help="Path to SQLite database")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to process")
    
    args = parser.parse_args()
    
    db_path = args.db
    if not db_path:
        workspace = get_workspace_root()
        db_path = os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "data", "water_well_directory.sqlite")
        
    enrich_counties(db_path, args.limit)
