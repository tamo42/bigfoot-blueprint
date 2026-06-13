import sqlite3
import json
import sys
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    db_file = script_dir.parent / "data" / "directory.sqlite"
    
    if not db_file.exists():
        print(f"Error: Database file '{db_file.name}' not found.")
        sys.exit(1)
        
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, name, latitude, longitude, phone, website_url, 
               reviews_json, profile_bio, speakable_bio, faq_json 
        FROM installers_haulers
    """)
    rows = c.fetchall()
    
    print(f"--- Database Integrity Verification ---")
    print(f"Database Path: {db_file}")
    print(f"Total Records: {len(rows)}\n")
    
    failures = 0
    
    for row in rows:
        row_id, name, lat, lng, phone, website, reviews, bio, speakable, faq = row
        record_errors = []
        
        # 1. Check coordinates
        if not lat or not lng:
            record_errors.append("Missing coordinates (latitude/longitude)")
        else:
            # Middle/North Georgia regional service area bounding box (includes Macon, Dublin, Conyers)
            if not (31.5 <= lat <= 34.0) or not (-85.0 <= lng <= -82.0):
                record_errors.append(f"Coordinates ({lat}, {lng}) out of service region bounds")
                
        # 2. Check phone
        if not phone:
            record_errors.append("Missing phone number")
            
        # 3. Check review snippets
        try:
            rev_list = json.loads(reviews) if reviews else []
            if not isinstance(rev_list, list):
                record_errors.append("reviews_json is not a JSON list")
        except Exception as e:
            record_errors.append(f"Failed to parse reviews_json: {e}")
            
        # 4. Check profile bio
        if not bio:
            record_errors.append("Missing profile_bio")
        elif len(bio.split()) < 150:
            record_errors.append(f"profile_bio is too short ({len(bio.split())} words)")
            
        # 5. Check speakable bio
        if not speakable:
            record_errors.append("Missing speakable_bio")
            
        # 6. Check FAQs
        try:
            faq_list = json.loads(faq) if faq else []
            if not isinstance(faq_list, list):
                record_errors.append("faq_json is not a JSON list")
            elif len(faq_list) != 20:
                record_errors.append(f"faq_json has {len(faq_list)} items instead of 20")
        except Exception as e:
            record_errors.append(f"Failed to parse faq_json: {e}")
            
        if record_errors:
            failures += 1
            print(f"[x] ID {row_id} - '{name}' failed verification:")
            for err in record_errors:
                print(f"    - {err}")
        else:
            print(f"[o] ID {row_id} - '{name}' verified successfully.")
            
    print(f"\nVerification finished.")
    if failures > 0:
        print(f"FAIL: {failures} records failed database integrity checks.")
        sys.exit(1)
    else:
        print("PASS: All records verified successfully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
