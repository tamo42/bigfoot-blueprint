import os
import re
import csv
import sqlite3
import sys
from datetime import datetime

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

def parse_srwmd_csv():
    csv_path = r"C:\Users\tamo4\Downloads\mysuwanneeriver water well contractors.csv"
    print(f"[*] Reading CSV file from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"[-] Error: CSV file not found at {csv_path}")
        return []
        
    contractors = []
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            license_num = row.get("License #", "").strip()
            name = row.get("Contractor Name", "").strip()
            county_raw = row.get("County", "").strip()
            phone = row.get("Phone", "").strip()
            email = row.get("E-Mail", "").strip()
            
            if not license_num or not name:
                continue
                
            # Parse county and state
            # Out of state examples: (GA), (SC), (NC)
            state = "FL"
            county = county_raw
            
            state_match = re.match(r'^\(([A-Z]{2})\)$', county_raw)
            if state_match:
                state = state_match.group(1)
                county = ""
                
            display_name = f"{name} Well Drilling"
            
            contractors.append({
                "license_number": license_num,
                "license_holder": name,
                "company_name": display_name,
                "phone": utils.clean_phone_number(phone),
                "county": county,
                "state": state,
                "email": email
            })
            
    print(f"[+] Parsed {len(contractors)} contractors from CSV.")
    return contractors

def main():
    import re
    db_path = utils.get_db_path("florida")
    print(f"[*] SQLite Database Path: {db_path}")
    
    # Initialize database tables
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    contractors = parse_srwmd_csv()
    if not contractors:
        print("[-] No records parsed. Exiting.")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    inserted_count = 0
    updated_count = 0
    
    for item in contractors:
        company_name = item["company_name"]
        
        # Check if this license number already exists in technician_licenses
        c.execute('''
            SELECT company_id 
            FROM technician_licenses 
            WHERE license_number = ?
        ''', (item["license_number"],))
        
        existing_license = c.fetchone()
        
        if existing_license:
            company_id = existing_license[0]
            # Since the license already exists, we update the existing listing's details
            # if we have a phone number or county and the existing one is empty.
            c.execute('SELECT phone_number, county FROM well_contractors WHERE id = ?', (company_id,))
            existing = c.fetchone()
            
            if existing:
                update_fields = []
                update_params = []
                
                if not existing[0] and item["phone"]:
                    update_fields.append("phone_number = ?")
                    update_params.append(item["phone"])
                if not existing[1] and item["county"]:
                    update_fields.append("county = ?")
                    update_params.append(item["county"])
                    
                if update_fields:
                    update_fields.extend(["date = ?", "data_freshness = ?"])
                    update_params.extend([current_date, current_date, company_id])
                    
                    c.execute(f'''
                        UPDATE well_contractors 
                        SET {", ".join(update_fields)} 
                        WHERE id = ?
                    ''', tuple(update_params))
            else:
                c.execute('''
                    UPDATE well_contractors 
                    SET date = ?, data_freshness = ? 
                    WHERE id = ?
                ''', (current_date, current_date, company_id))
                
            # Update technician license table details
            c.execute('''
                UPDATE technician_licenses
                SET license_holder = ?
                WHERE company_id = ? AND license_number = ?
            ''', (item["license_holder"], company_id, item["license_number"]))
            
            updated_count += 1
        else:
            # Generate slug
            slug = utils.slugify(company_name)
            
            # Handle slug collisions
            c.execute("SELECT id FROM well_contractors WHERE slug = ?", (slug,))
            if c.fetchone():
                slug = f"{slug}-{item['license_number']}"
            
            # Insert new parent record (with empty address fields, to be enriched by Google Places)
            c.execute('''
                INSERT INTO well_contractors 
                (name, slug, address, city, state, zip_code, county, phone_number, data_source, data_freshness, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name, slug, "", "", item["state"], "", item["county"], 
                item["phone"], "SRWMD", current_date, current_date
            ))
            
            company_id = c.lastrowid
            
            # Insert child license record
            c.execute('''
                INSERT INTO technician_licenses
                (company_id, license_holder, license_number, license_type, license_status, licensing_agency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                company_id, item["license_holder"], item["license_number"], 
                "Water Well Contractor", "Active", "SRWMD"
            ))
            
            inserted_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Scraping and Ingestion complete for SRWMD!")
    print(f"    - Inserted: {inserted_count} new listings")
    print(f"    - Updated: {updated_count} existing listings")

if __name__ == "__main__":
    main()
