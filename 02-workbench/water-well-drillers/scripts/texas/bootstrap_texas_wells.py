import os
import re
import sqlite3
import requests
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import utils
import schema

# Config
url = "https://data.texas.gov/resource/7358-krk7.json"
db_path = utils.get_db_path("texas")

def clean_name_and_company(raw_name):
    # Heuristic to clean name and build company name
    name = raw_name.strip().upper()
    if "," in name:
        parts = name.split(",", 1)
        last_name = parts[0].strip()
        first_name = parts[1].strip()
        
        # Reformat individual name
        formatted_name = f"{first_name} {last_name}".title()
        company_name = f"{formatted_name} Well Drilling & Pump Service"
        return formatted_name, company_name
    else:
        # It's already a company name or singular name
        formatted_name = name.title()
        company_name = formatted_name
        return formatted_name, company_name

def parse_city_state_zip(city_state_zip):
    if not city_state_zip:
        return None, None, None
    # Match: CITY STATE ZIP or CITY STATE ZIP-XXXX
    # e.g., "MIDLAND TX 79706-4018"
    match = re.match(r'^(.+)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', city_state_zip.strip())
    if match:
        city = match.group(1).strip().title()
        state = match.group(2).strip().upper()
        zip_code = match.group(3).strip()
        return city, state, zip_code
    return None, None, None

def bootstrap_texas():
    print("[*] Querying all active Texas Water Well Driller / Pump Installer records...")
    
    # SODA API: Request all matching records
    # limit = 2500 to fetch all active licenses in one request
    params = {
        "license_type": "Water Well Driller/Pump Installer",
        "$limit": 2500
    }
    
    try:
        res = requests.get(url, params=params, timeout=30)
        if res.status_code != 200:
            print(f"[-] Error querying TDLR API: {res.text[:500]}")
            return
            
        records = res.json()
        print(f"[+] Successfully fetched {len(records)} records from Texas Open Data Portal.")
        
    except Exception as e:
        print(f"[-] HTTP request failed: {e}")
        return

    # Initialize SQLite database using schema manager
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    print(f"[*] Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    inserted_count = 0
    ignored_count = 0

    for r in records:
        raw_name = r.get("business_name") or r.get("owner_name")
        if not raw_name:
            continue
            
        formatted_name, company_name = clean_name_and_company(raw_name)
        
        # Address
        addr1 = r.get("business_address_line1") or r.get("mailing_address_line1") or ""
        city_state_zip_raw = r.get("business_city_state_zip") or r.get("mailing_address_city_state_zip")
        
        city, state, zip_code = parse_city_state_zip(city_state_zip_raw)
        
        if not city:
            city = r.get("mailing_address_city")
            state = "TX"
            zip_code = None
            
        full_address = f"{addr1}, {city}, {state} {zip_code or ''}".strip(", ")
        county = r.get("business_county") or r.get("mailing_address_county") or ""
        county = county.strip().upper()
        
        phone = r.get("business_telephone") or r.get("owner_telephone") or ""
        formatted_phone = utils.clean_phone_number(phone)
        
        # License Info
        lic_num = r.get("license_number") or ""
        lic_subtype = r.get("license_subtype") or ""
        license_str = f"Water Well Driller/Pump Installer #{lic_num} (Subtype: {lic_subtype})"
        
        # Coordinates (Check if pre-geocoded coordinates are provided by SODA API)
        lat = None
        lng = None
        geo = r.get("business_mailing")
        if isinstance(geo, dict) and geo.get("type") == "Point":
            coords = geo.get("coordinates")
            if isinstance(coords, list) and len(coords) >= 2:
                # Socrata coordinates are [longitude, latitude]
                lng = coords[0]
                lat = coords[1]
        
        # Slugify
        slug = utils.slugify(company_name)
        
        # Verify slug uniqueness
        c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (slug,))
        if c.fetchone():
            slug = f"{slug}-{utils.slugify(city or 'texas')}"
            
        try:
            c.execute('''
                INSERT INTO installers_haulers 
                (name, slug, address, city, state, zip_code, county, phone_number, pumper_certification_level, manual_lat, manual_lng)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_name, slug, full_address, city, state, zip_code, county, formatted_phone, license_str, lat, lng))
            inserted_count += 1
        except sqlite3.IntegrityError:
            ignored_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Done bootstrapping Texas database!")
    print(f"    - Inserted records: {inserted_count}")
    print(f"    - Duplicate/ignored records: {ignored_count}")

if __name__ == "__main__":
    bootstrap_texas()
