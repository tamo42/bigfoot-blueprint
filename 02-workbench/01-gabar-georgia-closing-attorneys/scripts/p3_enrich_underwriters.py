import sqlite3
import json
import os
import argparse

# Database and Cache Configuration
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "data", "directory.sqlite")
CACHE_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "cache", "crawled_text", "01-gabar-georgia-closing-attorneys")

def scan_text_for_underwriters(text):
    appointments = []
    if not text:
        return appointments
        
    text_lower = text.lower()
    
    if "first american" in text_lower:
        appointments.append("First American Title")
    if "fidelity national" in text_lower or "chicago title" in text_lower or "commonwealth land" in text_lower:
        appointments.append("Fidelity National Title")
    if "stewart title" in text_lower:
        appointments.append("Stewart Title")
    if "old republic" in text_lower:
        appointments.append("Old Republic Title")
        
    return list(set(appointments))

def run_enrichment(limit=50):
    print("=========================================================")
    print(f"Georgia Closing Attorneys - Offline Underwriters Enrichment")
    print("=========================================================")
    print(f"Targeting batch limit: {limit}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Fetch records that previously yielded no results ('[]') AND have a website
    c.execute('''
        SELECT id, first_name, last_name, firm_name, city 
        FROM attorneys 
        WHERE appointments = '[]' AND website_url IS NOT NULL AND website_url != 'NOT_FOUND'
        LIMIT ?
    ''', (limit,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending records to enrich in this batch.")
        conn.close()
        return
        
    print(f"Found {len(records)} records to process.")
    
    for idx, row in enumerate(records):
        attorney_id = row['id']
        first_name = row['first_name']
        last_name = row['last_name']
        firm_name = row['firm_name'] or ""
        city = row['city']
        
        display_name = firm_name if firm_name else f"{first_name} {last_name}"
        print(f"\n[{idx+1}/{len(records)}] Processing ID {attorney_id}: {display_name} ({city})")
        
        cache_file = os.path.join(CACHE_DIR, f"{attorney_id}.txt")
        failed_file = os.path.join(CACHE_DIR, f"{attorney_id}.failed")
        
        if os.path.exists(failed_file):
            print(f"      [-] Crawl failed for this site previously. Skipping.")
            continue
        elif os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                content = f.read()
            appointments = scan_text_for_underwriters(content)
        else:
            print(f"      [-] No cache file found. You must run p3_crawl_websites.py first. Skipping.")
            continue
            
        if appointments:
            appointments_json = json.dumps(appointments)
            print(f"  [+] Discovered appointments: {appointments_json}")
            
            c.execute('''
                UPDATE attorneys
                SET appointments = ?
                WHERE id = ?
            ''', (appointments_json, attorney_id))
            
            conn.commit()
            print(f"  [+] Updated ID {attorney_id} in database.")
        else:
            print(f"  [-] No underwriters found in cached text.")
        
    conn.close()
    print("\n=========================================================")
    print("Underwriters Offline Enrichment Batch Complete!")
    print("=========================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich attorney records with underwriters offline from cache.")
    parser.add_argument("--limit", type=int, default=50, help="Number of records to process (default: 50)")
    args = parser.parse_args()
    
    run_enrichment(limit=args.limit)
