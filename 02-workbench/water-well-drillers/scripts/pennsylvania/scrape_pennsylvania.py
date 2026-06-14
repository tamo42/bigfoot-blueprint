import os
import sys
import urllib.request
import re
import ssl
import sqlite3
from html.parser import HTMLParser

# Import general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from general.utils import resolve_path, slugify, clean_phone_number, get_db_path
from general.schema import initialize_database

url = "https://www.iframeapps.dcnr.pa.gov/topogeo/LicensedDriller"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class DCNRParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.table_depth = 0
        self.current_tag = None
        self.drillers = []
        
        # State machine variables
        self.in_main_row = False
        self.main_row_cols = []
        self.in_td_or_th = False
        self.cell_content = []
        
        self.in_child_grid = False
        self.child_headers = []
        self.child_values = []
        self.current_child_details = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attr_dict = dict(attrs)
        
        if tag == "table":
            self.table_depth += 1
            if attr_dict.get("id") == "LicensedDrillerTable":
                self.in_table = True
            elif self.in_table and attr_dict.get("class") == "ChildGrid":
                self.in_child_grid = True
                self.child_headers = []
                self.child_values = []
                
        elif self.in_table:
            if tag == "tr":
                if not self.in_child_grid and self.table_depth == 1:
                    self.in_main_row = True
                    self.main_row_cols = []
                    self.current_child_details = None
            elif tag in ("td", "th"):
                self.in_td_or_th = True
                self.cell_content = []
                    
    def handle_data(self, data):
        if self.in_td_or_th:
            self.cell_content.append(data)
            
    def handle_endtag(self, tag):
        if self.in_table:
            if tag in ("td", "th"):
                self.in_td_or_th = False
                text = "".join(self.cell_content).strip()
                if self.in_child_grid:
                    if tag == "th":
                        self.child_headers.append(text)
                    elif tag == "td":
                        self.child_values.append(text)
                else:
                    if self.in_main_row:
                        self.main_row_cols.append(text)
                        
            elif tag == "tr":
                if self.in_main_row and not self.in_child_grid and self.table_depth == 1:
                    self.in_main_row = False
                    if len(self.main_row_cols) >= 5:
                        self.drillers.append({
                            "company": self.main_row_cols[1],
                            "city": self.main_row_cols[2],
                            "state": self.main_row_cols[3],
                            "phone": self.main_row_cols[4],
                            "details": self.current_child_details or {}
                        })
                        self.current_child_details = None
                        
            elif tag == "table":
                self.table_depth -= 1
                if self.in_child_grid and self.table_depth == 1:
                    self.in_child_grid = False
                    if self.child_headers and self.child_values:
                        details = {}
                        for h, v in zip(self.child_headers, self.child_values):
                            details[h] = v
                        self.current_child_details = details
                elif self.table_depth == 0:
                    self.in_table = False

def parse_address_fields(address_str):
    if not address_str:
        return "", "", "", ""
    
    # Match ZIP
    zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b$', address_str.strip())
    zip_code = zip_match.group(0) if zip_match else ""
    
    # Remove ZIP
    addr_no_zip = address_str.replace(zip_code, "").strip().rstrip(",")
    
    # Match State
    state_match = re.search(r'\b[A-Z]{2}\b$', addr_no_zip.strip())
    state = state_match.group(0) if state_match else ""
    
    # Remove State
    addr_no_state = addr_no_zip.replace(state, "").strip().rstrip(",")
    
    # Separate City and Street
    parts = addr_no_state.split(",")
    if len(parts) > 1:
        city = parts[-1].strip()
        street_address = ", ".join(parts[:-1]).strip()
    else:
        words = addr_no_state.split()
        if len(words) > 1:
            city = words[-1].strip()
            street_address = " ".join(words[:-1]).strip()
        else:
            city = addr_no_state
            street_address = addr_no_state
            
    return street_address, city, state, zip_code

def main():
    print("[*] Fetching Pennsylvania DCNR Well Drillers Roster...")
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"[-] Error downloading DCNR page: {e}")
        sys.exit(1)
        
    print("[*] Parsing HTML...")
    parser = DCNRParser()
    parser.feed(html)
    
    # Filter header row out
    raw_drillers = [d for d in parser.drillers if d["company"].lower() != "company"]
    print(f"[+] Successfully parsed {len(raw_drillers)} driller records.")
    
    # Initialize SQLite database
    db_path = get_db_path("pennsylvania")
    print(f"[*] Initializing SQLite database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    initialize_database(db_path)
    
    # Process and insert
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    inserted_count = 0
    updated_count = 0
    
    for d in raw_drillers:
        company = d["company"].strip()
        phone = clean_phone_number(d["phone"])
        
        details = d["details"]
        raw_address = details.get("Address", "")
        license_num = details.get("License #", "")
        services = details.get("Services Offered", "")
        counties = details.get("Counties Served", "")
        
        # Parse address
        street, city, state, zip_code = parse_address_fields(raw_address)
        
        # Fallbacks from main columns
        if not city:
            city = d["city"].strip()
        if not state:
            state = d["state"].strip()
            
        # Build clean slug
        driller_slug = slugify(f"{company} {city} {state}")
        
        # Prepare listing content from services
        listing_content = ""
        if services:
            listing_content = f"Services offered: {services}"
            
        # Select first county from list of served counties
        county = ""
        if counties:
            county = counties.split(",")[0].strip().title()
            
        # Insert or replace record
        try:
            # We want to check if slug exists
            c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (driller_slug,))
            row = c.fetchone()
            if row:
                # Update
                c.execute("""
                    UPDATE installers_haulers 
                    SET name=?, address=?, city=?, state=?, zip_code=?, county=?, phone_number=?, served_counties=?, listing_content=?, pumper_certification_level=?
                    WHERE id=?
                """, (company, street, city.title(), state.upper(), zip_code, county, phone, counties, listing_content, f"License #{license_num}" if license_num else None, row[0]))
                updated_count += 1
            else:
                # Insert
                c.execute("""
                    INSERT INTO installers_haulers (
                        name, slug, address, city, state, zip_code, county, phone_number, served_counties, listing_content, pumper_certification_level, coi_status, claimed, post_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Unverified', 0, 'publish')
                """, (company, driller_slug, street, city.title(), state.upper(), zip_code, county, phone, counties, listing_content, f"License #{license_num}" if license_num else None))
                inserted_count += 1
        except Exception as e:
            print(f"[-] Error inserting/updating record for '{company}': {e}")
            
    conn.commit()
    conn.close()
    
    print(f"\n[+] Database Sync Complete!")
    print(f"    Inserted: {inserted_count} new records")
    print(f"    Updated: {updated_count} existing records")
    
if __name__ == "__main__":
    main()
