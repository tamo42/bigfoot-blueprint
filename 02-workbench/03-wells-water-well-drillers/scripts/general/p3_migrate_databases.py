import os
import shutil
import sqlite3
import re
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import p3_utils as utils
import p3_schema as schema

def clean_phone(phone):
    if not phone:
        return ""
    return re.sub(r'[^\d]', '', str(phone))

def clean_website(url):
    if not url:
        return ""
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    return url.strip('/')

def is_company_name(name):
    """
    Returns True if the name contains common business suffixes or trade terms.
    """
    if not name:
        return False
    name_lower = name.lower()
    trade_terms = [
        "llc", "inc", "co", "corp", "company", "drilling", "pump", 
        "service", "brother", "son", "well", "water", "association", "contractor"
    ]
    return any(term in name_lower for term in trade_terms)

def parse_license_details(cert_string):
    """
    Parses legacy certification string to extract license number and type.
    """
    if not cert_string:
        return "", "CONTRACTOR"
    
    cert_string = str(cert_string).strip()
    match = re.match(r'^([A-Z0-9_]+)\s+#?(\d+)', cert_string, re.IGNORECASE)
    if match:
        license_type = match.group(1).upper()
        # Keep full string or number
        return cert_string, license_type
    
    # Keyword fallback
    if "driller" in cert_string.lower():
        license_type = "WELL_DRILLER"
    elif "pump" in cert_string.lower():
        license_type = "PUMP_INSTALLER"
    else:
        license_type = "CONTRACTOR"
        
    return cert_string, license_type

def migrate_and_consolidate():
    data_dir = utils.resolve_path("02-workbench/03-wells-water-well-drillers/data")
    unified_db_path = utils.get_unified_db_path()
    
    print("[*] Starting database consolidation migration...")
    print(f"[*] Unified Database Path: {unified_db_path}")
    
    # 1. Back up unified database if it exists
    if os.path.exists(unified_db_path):
        backup_dir = os.path.join(data_dir, "backup")
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(unified_db_path, os.path.join(backup_dir, "water_well_directory.sqlite.bak"))
        os.remove(unified_db_path)
        print("[+] Backed up and removed previous unified database.")
        
    # 2. Initialize the consolidated schema
    schema.initialize_database(unified_db_path)
    
    # 3. Read and group records from all state databases
    db_files = [f for f in os.listdir(data_dir) if f.endswith(".sqlite") and f != "water_well_directory.sqlite"]
    print(f"[*] Found {len(db_files)} state source databases to process.")
    
    # Global tracking dictionaries for grouping across databases
    # Key: group_key, Value: list of raw row dictionaries
    grouped_companies = {}
    
    total_raw_rows = 0
    
    for filename in db_files:
        db_path = os.path.join(data_dir, filename)
        state_prefix = filename.split("_")[0].lower()
        print(f"  [*] Processing state database: {filename}...")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if well_contractors or installers_haulers exists
            source_table = None
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='well_contractors'")
            if cursor.fetchone():
                source_table = "well_contractors"
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='installers_haulers'")
                if cursor.fetchone():
                    source_table = "installers_haulers"
            
            if not source_table:
                print(f"    [-] Skipping {filename}: neither well_contractors nor installers_haulers table found.")
                conn.close()
                continue
                
            cursor.execute(f"SELECT * FROM {source_table}")
            rows = cursor.fetchall()
            total_raw_rows += len(rows)
            
            for row in rows:
                row_dict = dict(row)
                row_dict["_state_prefix"] = state_prefix
                
                # Determine grouping key
                website = clean_website(row_dict.get("website_url"))
                phone = clean_phone(row_dict.get("phone_number"))
                name = row_dict.get("name") or ""
                city = row_dict.get("city") or ""
                
                group_key = None
                if website:
                    group_key = f"web:{website}"
                elif phone:
                    group_key = f"phone:{phone}"
                else:
                    slugified_name = utils.slugify(name)
                    slugified_city = utils.slugify(city)
                    group_key = f"name_city:{slugified_name}|{slugified_city}"
                    
                if group_key not in grouped_companies:
                    grouped_companies[group_key] = []
                grouped_companies[group_key].append(row_dict)
                
            conn.close()
            
        except Exception as e:
            print(f"    [-] Error reading {filename}: {e}")
            
    print(f"\n[*] Grouping complete:")
    print(f"    - Total raw source records processed: {total_raw_rows}")
    print(f"    - Total unique consolidated companies identified: {len(grouped_companies)}")
    
    # 4. Insert into the unified database
    conn_unified = sqlite3.connect(unified_db_path)
    cursor_unified = conn_unified.cursor()
    
    # Get columns list for well_contractors
    well_contractor_cols = [col[0] for col in schema.get_schema_columns()]
    placeholders = ", ".join(["?"] * len(well_contractor_cols))
    insert_company_query = f"INSERT INTO well_contractors ({', '.join(well_contractor_cols)}) VALUES ({placeholders})"
    
    insert_license_query = """
        INSERT INTO technician_licenses (company_id, license_holder, license_number, license_type, license_status, licensing_agency)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    inserted_companies = 0
    inserted_licenses = 0
    
    try:
        cursor_unified.execute("BEGIN TRANSACTION")
        
        for group_key, rows_list in grouped_companies.items():
            # Find the best row to represent the company profile
            # Prefer the one with a company-like name and most place data
            best_row = rows_list[0]
            for r in rows_list:
                if is_company_name(r.get("name")) and r.get("google_place_id"):
                    best_row = r
                    break
            else:
                # Secondary preference: company name
                for r in rows_list:
                    if is_company_name(r.get("name")):
                        best_row = r
                        break
                        
            # Prepare parent company values
            parent_values = []
            
            # Slug generation (must be unique)
            slug = best_row.get("slug") or utils.slugify(best_row.get("name") or "unnamed-contractor")
            # Append unique suffix if slug duplicate occurs in target
            original_slug = slug
            slug_suffix = 1
            while True:
                cursor_unified.execute("SELECT id FROM well_contractors WHERE slug = ?", (slug,))
                if not cursor_unified.fetchone():
                    break
                slug = f"{original_slug}-{slug_suffix}"
                slug_suffix += 1
                
            for col in well_contractor_cols:
                col_lower = col.lower()
                
                if col_lower == "id":
                    parent_values.append(None) # Auto-increment
                elif col_lower == "slug":
                    parent_values.append(slug)
                elif col_lower == "admin_category":
                    parent_values.append(best_row.get("admin_category") or "Water Well Contractor")
                elif col_lower == "admin_location":
                    parent_values.append(best_row.get("admin_location") or best_row.get("city"))
                elif col_lower in best_row:
                    parent_values.append(best_row[col_lower])
                else:
                    # Default values
                    if col_lower == "listing_tier":
                        parent_values.append("free")
                    elif col_lower in ("emergency_repair_247", "pressure_tank_services", "water_testing_offered", "residential_capable", "commercial_capable", "financing_available", "claimed", "featured"):
                        parent_values.append(0)
                    elif col_lower in ("google_rating", "google_review_count"):
                        parent_values.append(0)
                    else:
                        parent_values.append(None)
                        
            # Insert parent company
            cursor_unified.execute(insert_company_query, parent_values)
            company_id = cursor_unified.lastrowid
            inserted_companies += 1
            
            # Insert child licenses for all rows in the group
            for r in rows_list:
                # Parse license number & type
                cert_val = r.get("pumper_certification_level") or r.get("license_number") or ""
                license_num, license_type = parse_license_details(cert_val)
                
                # License holder name:
                # If name looks like a company name, holder might be empty or company name
                # If it looks like a person's name, it's the license holder.
                # To be safe and preserve original names, we insert the row's name as holder
                license_holder = r.get("name") or ""
                
                license_status = r.get("license_status") or "Active"
                licensing_agency = r.get("licensing_agency") or "State Health Dept"
                
                cursor_unified.execute(insert_license_query, (
                    company_id,
                    license_holder,
                    license_num,
                    license_type,
                    license_status,
                    licensing_agency
                ))
                inserted_licenses += 1
                
        cursor_unified.execute("COMMIT")
        print(f"\n[+] Unified database successfully consolidated and populated:")
        print(f"    - Inserted unique companies: {inserted_companies}")
        print(f"    - Inserted technician licenses: {inserted_licenses}")
        
    except Exception as e:
        cursor_unified.execute("ROLLBACK")
        print(f"[-] Consolidation failed: {e}")
        raise e
    finally:
        conn_unified.close()

if __name__ == "__main__":
    migrate_and_consolidate()
