import os
import sqlite3
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from scripts.general import p3_utils as utils
from scripts.general import p3_schema as schema
from scripts.general.p3_migrate_databases import clean_phone, clean_website, is_company_name, parse_license_details

def migrate_arizona():
    data_dir = os.path.abspath("data")
    unified_db_path = os.path.join(data_dir, "water_well_directory.sqlite")
    az_db_path = os.path.join(data_dir, "arizona_wells.sqlite")
    
    # 1. Initialize the consolidated schema
    schema.initialize_database(unified_db_path)
    
    # Read Arizona database
    conn_az = sqlite3.connect(az_db_path)
    conn_az.row_factory = sqlite3.Row
    cursor_az = conn_az.cursor()
    
    # Fetch from well_contractors
    cursor_az.execute("SELECT * FROM well_contractors")
    rows = cursor_az.fetchall()
    
    # 4. Insert into the unified database
    conn_unified = sqlite3.connect(unified_db_path)
    cursor_unified = conn_unified.cursor()
    
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
        
        for r in rows:
            row_dict = dict(r)
            row_dict["_state_prefix"] = "arizona"
            
            # Prepare parent company values
            parent_values = []
            
            # Slug generation
            slug = utils.slugify(row_dict.get("name") or "unnamed-contractor")
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
                    parent_values.append("Water Well Contractor")
                elif col_lower == "admin_location":
                    parent_values.append(row_dict.get("city"))
                elif col_lower in row_dict:
                    parent_values.append(row_dict[col_lower])
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
            
            # Insert child license
            cert_val = row_dict.get("roc_licenses") or row_dict.get("license_number") or ""
            license_num, license_type = parse_license_details(cert_val)
            
            license_holder = row_dict.get("qualifying_party") or ""
            license_status = row_dict.get("license_status") or "Active"
            licensing_agency = "ADWR"
            
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
        print(f"Appended {inserted_companies} companies and {inserted_licenses} licenses to master DB.")
        
    except Exception as e:
        cursor_unified.execute("ROLLBACK")
        print(f"Error: {e}")
        raise e
    finally:
        conn_unified.close()
        conn_az.close()

if __name__ == "__main__":
    migrate_arizona()
