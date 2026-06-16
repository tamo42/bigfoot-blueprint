import os
import sys
import urllib.request
import sqlite3
import re

# Add scripts/general to path to import p3_utils and p3_schema
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'general'))
import p3_schema as schema
import p3_utils as utils

DPOR_FILES = {
    "2701__crnt.txt": {"name": "Class A Contractor (Alt)", "is_general_contractor": True},
    "2705a__crnt.txt": {"name": "Class A Contractor", "is_general_contractor": True},
    "2705b__crnt.txt": {"name": "Class B Contractor", "is_general_contractor": True},
    "2705c__crnt.txt": {"name": "Class C Contractor", "is_general_contractor": True},
    "2719__crnt.txt": {"name": "Certified Water Well Systems Provider", "is_general_contractor": False}
}

BASE_URL = "https://www.dpor.virginia.gov/sites/default/files/Records%20and%20Documents/Regulant%20List/"

def download_file(url, dest_path):
    """
    Downloads a large file using chunked streaming to prevent high memory usage.
    """
    print(f"[*] Downloading {url} to {dest_path}...")
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        with open(dest_path, 'wb') as f:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                sys.stdout.write(".")
                sys.stdout.flush()
    print("\n[+] Download complete.")

def main():
    db_path = utils.get_db_path("virginia")
    schema.initialize_database(db_path)
    
    workspace_root = utils.get_workspace_root()
    cache_dir = os.path.join(workspace_root, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    well_drillers = {}
    email_regex = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    
    for filename, config in DPOR_FILES.items():
        print(f"\n=== Processing {config['name']} ({filename}) ===")
        local_txt_path = os.path.join(cache_dir, f"virginia_{filename}")
        
        # 1. Download file streamingly if not already cached
        if not os.path.exists(local_txt_path):
            download_file(BASE_URL + filename, local_txt_path)
        else:
            print(f"[+] Using cached regulant file: {local_txt_path}")
            
        file_line_count = 0
        file_match_count = 0
        
        with open(local_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                file_line_count += 1
                
                # Skip header row if present
                if file_line_count == 1 and "BOARD" in line:
                    continue
                    
                parts = line.strip('\r\n').split('\t')
                
                if len(parts) < 19:
                    continue
                    
                classifications = parts[18].strip().upper()
                
                # Filter Logic:
                # - General Contractor files: must have a specialty starting with "WW"
                # - Certified Water Well Systems Provider file: every row is a well provider
                if config['is_general_contractor']:
                    specialty_tokens = set(classifications.split())
                    is_well_driller = any(tok.startswith('WW') for tok in specialty_tokens)
                    if not is_well_driller:
                        continue
                
                file_match_count += 1
                
                # Reconstruct license number
                board_code = parts[0].strip()
                license_prefix = parts[1].strip()
                license_suffix = parts[2].strip()
                license_number = f"{board_code}{license_prefix}{license_suffix}"
                
                # Determine Name
                indiv_name = parts[3].strip()
                bus_name = parts[4].strip()
                name = bus_name if bus_name else indiv_name
                
                if not name:
                    continue
                
                # Handle address
                addr_parts = [parts[5].strip(), parts[6].strip(), parts[7].strip()]
                address = " ".join([p for p in addr_parts if p])
                
                city = parts[8].strip()
                state = parts[9].strip()
                
                # Format Zip Code
                zip_val = parts[10].strip()
                zip_plus4 = parts[11].strip()
                if zip_plus4 and zip_plus4 != '0000':
                    zip_code = f"{zip_val}-{zip_plus4}"
                else:
                    zip_code = zip_val
                    
                # Expiry and issue dates
                expiry_date = parts[15].strip() if len(parts) > 15 else ""
                issue_date = parts[16].strip() if len(parts) > 16 else ""
                contractor_class = parts[17].strip() if len(parts) > 17 else ""
                
                # Check for email in parts[19] or other trailing parts
                email = ""
                for p in parts[19:]:
                    p_clean = p.strip()
                    if email_regex.search(p_clean):
                        email = p_clean
                        break
                        
                # Build listing content details
                content_lines = [
                    f"**Virginia Contractor License:** {license_number}",
                    f"**Contractor Class:** Class {contractor_class}" if contractor_class else "",
                    f"**Specialties & Classifications:** {classifications}" if classifications else "**Specialty:** Certified Water Well Systems Provider",
                    f"**License Issue Date:** {issue_date}" if issue_date else "",
                    f"**License Expiration Date:** {expiry_date}" if expiry_date else "",
                ]
                if email:
                    content_lines.append(f"**Email:** {email}")
                    
                listing_content = "\n".join([line for line in content_lines if line])
                
                # Deduplicate by license_number
                if license_number not in well_drillers:
                    well_drillers[license_number] = {
                        'name': name,
                        'license_number': license_number,
                        'address': address,
                        'city': city,
                        'state': state,
                        'zip_code': zip_code,
                        'listing_content': listing_content,
                        'classifications': classifications
                    }
                    
            print(f"[+] File scan completed. Scanned {file_line_count} rows. Found {file_match_count} records.")

    print(f"\n[+] Total unique well contractors compiled: {len(well_drillers)}")
    
    # Ingest into SQLite database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    inserted = 0
    updated = 0
    
    for license_number, driller in well_drillers.items():
        slug = utils.slugify(f"{driller['name']} {driller['state']}")
        
        # Check if slug exists
        c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (slug,))
        row = c.fetchone()
        
        if row:
            # Update
            c.execute("""
                UPDATE installers_haulers
                SET name = ?, address = ?, city = ?, state = ?, zip_code = ?, listing_content = ?, coi_status = ?
                WHERE id = ?
            """, (
                driller['name'],
                driller['address'],
                driller['city'],
                driller['state'],
                driller['zip_code'],
                driller['listing_content'],
                'Verified' if driller['license_number'] else 'Unverified',
                row[0]
            ))
            updated += 1
        else:
            # Insert
            c.execute("""
                INSERT INTO installers_haulers 
                (name, slug, address, city, state, zip_code, listing_content, coi_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                driller['name'],
                slug,
                driller['address'],
                driller['city'],
                driller['state'],
                driller['zip_code'],
                driller['listing_content'],
                'Verified' if driller['license_number'] else 'Unverified'
            ))
            inserted += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Ingestion completed. Inserted: {inserted}, Updated: {updated} in {db_path}")

if __name__ == '__main__':
    main()
