import os
import re
import sqlite3
import pypdf
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import utils
import schema

# Config
pdf_path = utils.resolve_path(r"cache\ohio_registered_pws_contractors.pdf")
db_path = utils.get_db_path("ohio")

def parse_city_state_zip(text):
    match = re.match(r'^([^,]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', text.strip())
    if match:
        city = match.group(1).strip().title()
        state = match.group(2).strip().upper()
        zip_code = match.group(3).strip()
        return city, state, zip_code
    return None, None, None

def extract_services(first_line_col4):
    services = []
    line_len = len(first_line_col4)
    
    def has_x(start, end):
        rel_start = start - 110
        rel_end = end - 110
        if rel_start >= line_len:
            return False
        segment = first_line_col4[rel_start:min(rel_end, line_len)].upper()
        return 'X' in segment

    if has_x(115, 124): services.append("Well")
    if has_x(124, 134): services.append("Spring")
    if has_x(134, 143): services.append("Pump")
    if has_x(143, 153): services.append("Water")
    if has_x(153, 163): services.append("Cistern")
    if has_x(163, 173): services.append("Pond")
    if has_x(173, 185): services.append("Sealing")
    
    return services

def process_block(block_lines, county):
    if not block_lines:
        return None
        
    first_line = block_lines[0]
    
    # 1. License Number
    col1_first = first_line[0:45].strip()
    license_match = re.search(r'\d{4}-PWSC-\d{2}-\d{6}', col1_first)
    if not license_match:
        return None
    license_num = license_match.group(0)
    
    # 2. Registration Year
    reg_year = ""
    if len(block_lines) > 1:
        col1_second = block_lines[1][0:45].strip()
        year_match = re.search(r'\d{4}', col1_second)
        if year_match:
            reg_year = year_match.group(0)
            
    # 3. Column 2: Company Name and Address lines
    col2_lines = []
    for line in block_lines:
        col2_val = line[45:80].strip()
        if col2_val:
            col2_lines.append(col2_val)
            
    if len(col2_lines) < 2:
        return None
        
    city_state_zip_raw = col2_lines[-1]
    city, state, zip_code = parse_city_state_zip(city_state_zip_raw)
    
    street_address = col2_lines[-2]
    
    company_lines = col2_lines[:-2]
    if company_lines:
        company_name = " ".join(company_lines).strip()
    else:
        company_name = street_address
        street_address = ""
        
    # 4. Column 3: Contact Name, Phone, and Registration Date
    col3_lines = []
    for line in block_lines:
        col3_val = line[80:110].strip()
        if col3_val:
            col3_lines.append(col3_val)
            
    owner_name = col3_lines[0] if len(col3_lines) > 0 else ""
    phone_number = col3_lines[1] if len(col3_lines) > 1 else ""
    
    # Clean phone number using utils helper
    phone_number = utils.clean_phone_number(phone_number)
        
    reg_date = ""
    for val in col3_lines[2:]:
        if re.search(r'[A-Za-z]+\s+\d{1,2},\s+\d{4}', val):
            reg_date = val
            break
            
    # 5. Column 4: Services
    first_line_col4 = first_line[110:]
    services = extract_services(first_line_col4)
    services_str = ", ".join(services)
    
    license_str = f"Ohio PWSC #{license_num}"
    if reg_year:
        license_str += f" (Registered {reg_year})"
        
    full_address = f"{street_address}, {city_state_zip_raw}".strip(", ")
    
    return {
        "name": company_name,
        "address": full_address,
        "city": city or "",
        "state": state or "OH",
        "zip_code": zip_code or "",
        "county": county,
        "phone_number": phone_number,
        "pumper_certification_level": license_str,
        "served_counties": services_str,
        "owner_name": owner_name,
        "registration_date": reg_date
    }

def main():
    if not os.path.exists(pdf_path):
        print(f"[-] Error: File not found: {pdf_path}")
        return

    print(f"[*] Checking for header byte signature pollution in: {pdf_path}...")
    with open(pdf_path, 'rb') as f:
        data = f.read()
        
    pdf_sig = b'%PDF-'
    sig_idx = data.find(pdf_sig)
    
    clean_temp_path = pdf_path + ".clean"
    pdf_to_read = pdf_path
    
    if sig_idx > 0:
        print(f"[*] Stripping {sig_idx} bytes of header pollution (e.g. injected scripts) preceding %PDF-...")
        with open(clean_temp_path, 'wb') as f_clean:
            f_clean.write(data[sig_idx:])
        pdf_to_read = clean_temp_path
        
    print(f"[*] Parsing Ohio PDF: {pdf_to_read}...")
    reader = pypdf.PdfReader(pdf_to_read)
    
    contractors = []
    current_county = "Unknown"
    current_block = []
    
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text(extraction_mode="layout")
        lines = text.split("\n")
        
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            # Detect county name (starts with 4 spaces exactly)
            if line.startswith('    ') and not line.startswith('     '):
                if not any(clean_line.startswith(x) for x in ["Total for", "Ohio", "Contractor", "dEDate", "PAGE", "---"]):
                    if current_block:
                        res = process_block(current_block, current_county)
                        if res:
                            contractors.append(res)
                        current_block = []
                        
                    current_county = clean_line.strip()
                    continue
            
            # Detect start of a new contractor block
            col1_text = line[0:45].strip()
            is_new_block = bool(re.search(r'\d{4}-PWSC-\d{2}-\d{6}', col1_text))
            
            if is_new_block:
                if current_block:
                    res = process_block(current_block, current_county)
                    if res:
                        contractors.append(res)
                current_block = [line]
            else:
                if current_block:
                    if "Total for" in clean_line or re.search(r'\d{2}/\d{2}/\d{4}', clean_line) or "of 104" in clean_line:
                        res = process_block(current_block, current_county)
                        if res:
                            contractors.append(res)
                        current_block = []
                    else:
                        current_block.append(line)
                        
        if current_block:
            res = process_block(current_block, current_county)
            if res:
                contractors.append(res)
            current_block = []

    print(f"[+] Successfully parsed {len(contractors)} contractors.")

    # Remove the cleaned temporary PDF if it was created
    if os.path.exists(clean_temp_path):
        os.remove(clean_temp_path)

    # Save to SQLite using centralized schema manager
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    print(f"[*] Connecting to SQLite database: {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    inserted = 0
    ignored = 0
    for co in contractors:
        slug = utils.slugify(co["name"])
        c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (slug,))
        if c.fetchone():
            slug = f"{slug}-{utils.slugify(co['city'] or 'ohio')}"
            
        try:
            c.execute('''
                INSERT INTO installers_haulers 
                (name, slug, address, city, state, zip_code, county, phone_number, pumper_certification_level, served_counties, listing_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                co["name"], slug, co["address"], co["city"], co["state"], co["zip_code"], 
                co["county"], co["phone_number"], co["pumper_certification_level"], co["served_counties"],
                f"Contact: {co['owner_name']}" if co['owner_name'] else None
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            ignored += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Successfully bootstrapped Ohio database!")
    print(f"    - Inserted records: {inserted}")
    print(f"    - Ignored duplicates: {ignored}")

if __name__ == "__main__":
    main()
