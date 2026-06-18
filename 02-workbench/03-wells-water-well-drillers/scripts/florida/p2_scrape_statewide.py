import os
import csv
import sqlite3
import sys
import re
from datetime import datetime

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

def parse_statewide_csv():
    csv_path = r"C:\Users\tamo4\Downloads\cntrctr_export_1781738905705.csv"
    print(f"[*] Reading statewide CSV file from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"[-] Error: CSV file not found at {csv_path}")
        return []
        
    contractors = []
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Note the typos or header variations
            license_num = row.get("License #", "").strip()
            status = row.get("Status", "").strip()
            contractor_name = row.get("Contrator Name", "").strip()
            business_name = row.get("Business Name", "").strip()
            city = row.get("City Name", "").strip()
            phone = row.get("Phone No", "").strip()
            email = row.get("Email Address", "").strip()
            county_raw = row.get("County", "").strip()
            district = row.get("Issuing District", "").strip()
            
            if not license_num or not contractor_name:
                continue
                
            # If business name is blank, default to [Contractor Name] Well Drilling
            display_name = business_name if business_name else f"{contractor_name} Well Drilling"
            
            # Clean county: if it's a list, we capture the first one for primary county
            # and we keep the rest for reference.
            primary_county = ""
            served_counties = ""
            if county_raw:
                counties = [c.strip() for c in county_raw.split(',') if c.strip()]
                if counties:
                    primary_county = counties[0]
                    served_counties = ", ".join(counties)
            
            contractors.append({
                "license_number": license_num,
                "license_holder": contractor_name,
                "company_name": display_name,
                "city": city,
                "phone": utils.clean_phone_number(phone),
                "email": email,
                "county": primary_county,
                "served_counties": served_counties,
                "district": district,
                "status": status
            })
            
    print(f"[+] Parsed {len(contractors)} contractors from CSV.")
    return contractors

def main():
    db_path = utils.get_db_path("florida")
    print(f"[*] SQLite Database Path: {db_path}")
    
    # Initialize database tables
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    contractors = parse_statewide_csv()
    if not contractors:
        print("[-] No records parsed. Exiting.")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    
    for item in contractors:
        # Check if this license number already exists in technician_licenses
        c.execute('''
            SELECT company_id 
            FROM technician_licenses 
            WHERE license_number = ?
        ''', (item["license_number"],))
        
        existing_license = c.fetchone()
        
        if existing_license:
            company_id = existing_license[0]
            
            # Get existing values
            c.execute('SELECT phone_number, county, city, data_source FROM well_contractors WHERE id = ?', (company_id,))
            existing = c.fetchone()
            
            if existing:
                update_fields = []
                update_params = []
                
                # Update empty fields with CSV data
                if not existing[0] and item["phone"]:
                    update_fields.append("phone_number = ?")
                    update_params.append(item["phone"])
                if not existing[1] and item["county"]:
                    update_fields.append("county = ?")
                    update_params.append(item["county"])
                if not existing[2] and item["city"]:
                    update_fields.append("city = ?")
                    update_params.append(item["city"])
                if (not existing[3] or existing[3] in ["SWFWMD", "SFWMD", "SRWMD"]) and item["district"]:
                    # Keep district tracker if multiple WMDs cover it
                    update_fields.append("data_source = ?")
                    update_params.append(item["district"])
                    
                if update_fields:
                    update_fields.extend(["date = ?", "data_freshness = ?"])
                    update_params.extend([current_date, current_date, company_id])
                    
                    c.execute(f'''
                        UPDATE well_contractors 
                        SET {", ".join(update_fields)} 
                        WHERE id = ?
                    ''', tuple(update_params))
                    
            # Update license details
            c.execute('''
                UPDATE technician_licenses
                SET license_holder = ?, license_status = ?, licensing_agency = ?
                WHERE company_id = ? AND license_number = ?
            ''', (item["license_holder"], item["status"], item["district"], company_id, item["license_number"]))
            
            updated_count += 1
        else:
            # Generate slug
            slug = utils.slugify(item["company_name"])
            
            # Handle slug collisions
            c.execute("SELECT id FROM well_contractors WHERE slug = ?", (slug,))
            if c.fetchone():
                slug = f"{slug}-{item['license_number']}"
            
            # Insert new parent record
            c.execute('''
                INSERT INTO well_contractors 
                (name, slug, address, city, state, zip_code, county, served_counties, phone_number, data_source, data_freshness, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item["company_name"], slug, "", item["city"], "FL", "", 
                item["county"], item["served_counties"], item["phone"], 
                item["district"], current_date, current_date
            ))
            
            company_id = c.lastrowid
            
            # Insert child license record
            c.execute('''
                INSERT INTO technician_licenses
                (company_id, license_holder, license_number, license_type, license_status, licensing_agency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                company_id, item["license_holder"], item["license_number"], 
                "Water Well Contractor", item["status"], item["district"]
            ))
            
            inserted_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Ingestion complete for Florida Statewide Data!")
    print(f"    - Inserted: {inserted_count} new listings")
    print(f"    - Updated: {updated_count} existing listings")

if __name__ == "__main__":
    main()
