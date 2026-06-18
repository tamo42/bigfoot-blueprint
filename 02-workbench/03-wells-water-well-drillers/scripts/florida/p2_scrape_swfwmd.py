import os
import re
import sqlite3
import sys
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

def fetch_and_parse_contractors():
    url = "https://www.swfwmd.state.fl.us/epermitting/well-contractors"
    print(f"[*] Fetching contractor list from {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[-] Error downloading page: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the table inside .view-well-contractors
    table = soup.select(".view-well-contractors table")
    if not table:
        # Fallback to general table search if wrapper class changes
        table = soup.find_all("table")
        if not table:
            print("[-] Error: No table found on the page.")
            return []
        table = [table[0]]
        
    table = table[0]
    rows = table.find("tbody").find_all("tr")
    print(f"[+] Found {len(rows)} raw rows in table.")
    
    contractors = []
    
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
            
        license_num = cells[0].text.strip()
        contractor_name = cells[1].text.strip()
        dba_name = cells[2].text.strip()
        street = cells[3].text.strip()
        city = cells[4].text.strip()
        state = cells[5].text.strip()
        zip_code = cells[6].text.strip()
        
        # Phone can be plain text or a tel link
        phone_cell = cells[7]
        phone_link = phone_cell.find("a")
        phone = phone_link.text.strip() if phone_link else phone_cell.text.strip()
        
        # Determine the primary display name for the listing
        # If DBA/Company name is present, use it. Otherwise, use contractor name.
        display_name = dba_name if dba_name else f"{contractor_name} Well Drilling".strip()
        
        contractors.append({
            "license_number": license_num,
            "license_holder": contractor_name,
            "company_name": display_name,
            "street": street,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "phone": utils.clean_phone_number(phone)
        })
        
    return contractors

def main():
    db_path = utils.get_db_path("florida")
    print(f"[*] SQLite Database Path: {db_path}")
    
    # Initialize database tables
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    contractors = fetch_and_parse_contractors()
    if not contractors:
        print("[-] No records parsed. Exiting.")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    inserted_count = 0
    updated_count = 0
    
    for item in contractors:
        # Build clean address
        street = item["street"]
        city = item["city"]
        state = item["state"]
        zip_code = item["zip_code"]
        full_address = f"{street}, {city}, {state} {zip_code}"
        
        company_name = item["company_name"]
        slug = utils.slugify(company_name)
        
        # Check if the listing already exists (deduplicating by license_number + street_address to support branch offices)
        # We look up in technician_licenses to find matching license number first,
        # then check if parent listing has the same street address.
        c.execute('''
            SELECT wc.id, wc.slug 
            FROM well_contractors wc
            JOIN technician_licenses tl ON wc.id = tl.company_id
            WHERE tl.license_number = ? AND wc.address = ?
        ''', (item["license_number"], full_address))
        
        existing = c.fetchone()
        
        if existing:
            company_id = existing[0]
            # Update existing parent record details
            c.execute('''
                UPDATE well_contractors
                SET name = ?, phone_number = ?, date = ?, data_freshness = ?
                WHERE id = ?
            ''', (company_name, item["phone"], current_date, current_date, company_id))
            
            # Update license status/holder details
            c.execute('''
                UPDATE technician_licenses
                SET license_holder = ?
                WHERE company_id = ? AND license_number = ?
            ''', (item["license_holder"], company_id, item["license_number"]))
            
            updated_count += 1
        else:
            # Handle slug collisions
            c.execute("SELECT id FROM well_contractors WHERE slug = ?", (slug,))
            if c.fetchone():
                slug = f"{slug}-{utils.slugify(city)}"
                # If still collides, append license number
                c.execute("SELECT id FROM well_contractors WHERE slug = ?", (slug,))
                if c.fetchone():
                    slug = f"{slug}-{item['license_number']}"
            
            # Insert new parent record
            c.execute('''
                INSERT INTO well_contractors 
                (name, slug, address, city, state, zip_code, phone_number, data_source, data_freshness, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name, slug, full_address, city, state, zip_code, 
                item["phone"], "SWFWMD", current_date, current_date
            ))
            
            company_id = c.lastrowid
            
            # Insert child license record
            c.execute('''
                INSERT INTO technician_licenses
                (company_id, license_holder, license_number, license_type, license_status, licensing_agency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                company_id, item["license_holder"], item["license_number"], 
                "Water Well Contractor", "Active", "SWFWMD"
            ))
            
            inserted_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Scraping and Ingestion complete for SWFWMD!")
    print(f"    - Inserted: {inserted_count} new listings")
    print(f"    - Updated: {updated_count} existing listings")

if __name__ == "__main__":
    main()
