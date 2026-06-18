import os
import re
import sqlite3
import sys
from datetime import datetime
import requests
import pypdf

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

def download_pdf():
    pdf_url = "https://www.sfwmd.gov/sites/default/files/documents/SFWMD_Contractor_List_Active_09222025.pdf"
    cache_dir = utils.resolve_path("02-workbench/03-wells-water-well-drillers/cache")
    os.makedirs(cache_dir, exist_ok=True)
    pdf_path = os.path.join(cache_dir, "sfwmd_active.pdf")
    
    if os.path.exists(pdf_path):
        print(f"[+] Using cached PDF at {pdf_path}")
        return pdf_path
        
    print(f"[*] Downloading PDF from {pdf_url}...")
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print(f"[+] Downloaded PDF to {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"[-] Error downloading PDF: {e}")
        return None

def split_phone_and_biz(rest):
    parts = rest.split()
    phone_parts = []
    biz_parts = []
    found_biz = False
    
    for part in parts:
        if found_biz:
            biz_parts.append(part)
            continue
            
        part_clean = part.lower().strip("(),")
        if (any(c.isdigit() for c in part) or 
            part_clean in ["or", "ext", "c", "o", "c/o", "cell", "office", "work", "fax"]):
            phone_parts.append(part)
        else:
            found_biz = True
            biz_parts.append(part)
            
    return " ".join(phone_parts), " ".join(biz_parts)

def parse_sfwmd_pdf(pdf_path):
    print(f"[*] Parsing PDF: {pdf_path}...")
    reader = pypdf.PdfReader(pdf_path)
    
    start_pattern = re.compile(r'^\s*(\d+)\s+(.*?)$')
    date_pattern = re.compile(r'^(.*?)\s+(\d{1,2}/\d{1,2}/\d{4})(?:\s+(.*))?$')
    
    contractors = []
    
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.split('\n')
        
        for line in lines:
            line_str = line.strip()
            if not line_str or "Active Well Contractor List" in line_str or "Contractor Number" in line_str or "9/22/25" in line_str or "Page" in line_str:
                continue
                
            start_match = start_pattern.match(line_str)
            if not start_match:
                continue
                
            license_num = start_match.group(1)
            remaining = start_match.group(2).strip()
            
            date_match = date_pattern.match(remaining)
            if not date_match:
                continue
                
            name = date_match.group(1).strip()
            exp_date = date_match.group(2)
            rest = date_match.group(3).strip() if date_match.group(3) else ""
            
            email = ""
            phone = ""
            biz_name = ""
            
            if rest:
                email_match = re.search(r'\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})$', rest)
                if email_match:
                    email = email_match.group(1).strip()
                    rest = rest[:email_match.start()].strip()
                
                phone, biz_name = split_phone_and_biz(rest)
            
            display_name = biz_name if biz_name else f"{name} Well Drilling".strip()
            
            contractors.append({
                "license_number": license_num,
                "license_holder": name,
                "company_name": display_name,
                "phone": utils.clean_phone_number(phone),
                "email": email
            })
            
    print(f"[+] Extracted {len(contractors)} contractors from PDF.")
    return contractors

def main():
    db_path = utils.get_db_path("florida")
    print(f"[*] SQLite Database Path: {db_path}")
    
    # Initialize database tables
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    pdf_path = download_pdf()
    if not pdf_path:
        print("[-] PDF download failed. Exiting.")
        return
        
    contractors = parse_sfwmd_pdf(pdf_path)
    if not contractors:
        print("[-] No records parsed from PDF. Exiting.")
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
            # if we have a phone number and the existing one is empty.
            c.execute('SELECT phone_number FROM well_contractors WHERE id = ?', (company_id,))
            existing_phone = c.fetchone()
            
            if existing_phone and not existing_phone[0] and item["phone"]:
                c.execute('''
                    UPDATE well_contractors 
                    SET phone_number = ?, date = ?, data_freshness = ? 
                    WHERE id = ?
                ''', (item["phone"], current_date, current_date, company_id))
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
                (name, slug, address, city, state, zip_code, phone_number, data_source, data_freshness, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name, slug, "", "", "FL", "", 
                item["phone"], "SFWMD", current_date, current_date
            ))
            
            company_id = c.lastrowid
            
            # Insert child license record
            c.execute('''
                INSERT INTO technician_licenses
                (company_id, license_holder, license_number, license_type, license_status, licensing_agency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                company_id, item["license_holder"], item["license_number"], 
                "Water Well Contractor", "Active", "SFWMD"
            ))
            
            inserted_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Scraping and Ingestion complete for SFWMD!")
    print(f"    - Inserted: {inserted_count} new listings")
    print(f"    - Updated: {updated_count} existing listings")

if __name__ == "__main__":
    main()
