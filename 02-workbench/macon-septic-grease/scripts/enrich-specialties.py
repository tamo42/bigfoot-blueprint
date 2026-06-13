import os
import sqlite3
import argparse
import time
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path

# Keyword matrices for specialty classifications
KEYWORDS = {
    "specialty_grease_trap": [
        "grease trap", "grease interceptor", "grease removal", 
        "fog removal", "kitchen grease", "grease trap cleaning", 
        "grease pumping", "restaurant grease"
    ],
    "specialty_septic_pump": [
        "septic tank", "septic pump", "septic cleaning", 
        "septic pumping", "septage", "septic inspection",
        "pump septic", "clean septic"
    ],
    "specialty_riser_install": [
        "riser", "risers", "septic lid", "septic cover", 
        "concrete riser", "riser installation"
    ],
    "specialty_line_jetting": [
        "hydro jetting", "line jetting", "high pressure jetting", 
        "water jetting", "jetting", "hydro-jetting"
    ],
    "specialty_inspections": [
        "inspection", "inspections", "real estate letter", 
        "septic certification", "dye test", "septic letter"
    ],
    "specialty_emergency_dispatch": [
        "24/7", "emergency service", "emergency pumping", 
        "emergency backup", "same day", "emergency drain"
    ]
}

def crawl_and_classify(url):
    results = {k: 0 for k in KEYWORDS.keys()}
    if not url:
        return results
        
    print(f"Crawling URL: {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Fetch the homepage
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        page_text = soup.get_text().lower()
        
        # Classify based on keyword match
        for specialty, kw_list in KEYWORDS.items():
            for kw in kw_list:
                if kw in page_text:
                    print(f"  [+] Match found for {specialty}: '{kw}'")
                    results[specialty] = 1
                    break # Stop checking once a match is found for this specialty
                    
    except Exception as e:
        print(f"  [!] Scrape error: {e}")
        # Return default zeros on failure, crawler flag will still be updated
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Classify provider specialties by scraping homepages.")
    parser.add_argument("--limit", type=int, default=5, help="Limit the number of records to process (default: 5)")
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    db_file = script_dir.parent / "data" / "directory.sqlite"
    
    if not db_file.exists():
        print(f"Error: Database file '{db_file.name}' not found. Run import-seed.py first.")
        return
        
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Query records where specialties have not been crawled
    c.execute("""
        SELECT id, name, website_url 
        FROM installers_haulers 
        WHERE specialties_crawled = 0
        LIMIT ?
    """, (args.limit,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending uncrawled records found in database.")
        conn.close()
        return
        
    print(f"Processing specialties for {len(records)} records (Limit: {args.limit})...")
    
    for i, row in enumerate(records):
        record_id = row["id"]
        name = row["name"]
        website_url = row["website_url"]
        
        print(f"\n[{i+1}/{len(records)}] Analyzing: '{name}'")
        
        if website_url:
            specialties = crawl_and_classify(website_url)
        else:
            print("  [-] No website URL listed. Skipping crawl.")
            specialties = {k: 0 for k in KEYWORDS.keys()}
            
        # Update columns in SQLite
        c.execute("""
            UPDATE installers_haulers
            SET specialty_grease_trap = ?,
                specialty_septic_pump = ?,
                specialty_riser_install = ?,
                specialty_line_jetting = ?,
                specialty_inspections = ?,
                specialty_emergency_dispatch = ?,
                specialties_crawled = 1
            WHERE id = ?
        """, (
            specialties["specialty_grease_trap"],
            specialties["specialty_septic_pump"],
            specialties["specialty_riser_install"],
            specialties["specialty_line_jetting"],
            specialties["specialty_inspections"],
            specialties["specialty_emergency_dispatch"],
            record_id
        ))
        
        conn.commit()
        print(f"  [+] Updated classifications for ID {record_id} in database.")
        
        # Jitter delay
        if website_url:
            time.sleep(1.0)
            
    conn.close()
    print("\nSpecialty Classification Batch Complete.")

if __name__ == "__main__":
    main()
