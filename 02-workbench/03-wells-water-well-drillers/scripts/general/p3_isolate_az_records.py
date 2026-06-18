import sqlite3
import os

MASTER_DB = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\data\water_well_directory.sqlite"
STATE_DB = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\data\arizona_isolated_wells.sqlite"

def main():
    if os.path.exists(STATE_DB):
        os.remove(STATE_DB)
        
    print(f"[*] Extracting unenriched AZ records from master database to: {STATE_DB}")
    
    # 1. Initialize schema in the local isolated state db
    import sys
    sys.path.append(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\scripts\general")
    import p3_schema
    p3_schema.initialize_database(STATE_DB)
    
    # 2. Query and transfer
    conn_m = sqlite3.connect(MASTER_DB)
    conn_m.row_factory = sqlite3.Row
    c_m = conn_m.cursor()
    
    conn_s = sqlite3.connect(STATE_DB)
    c_s = conn_s.cursor()
    
    # Query all unenriched AZ records
    c_m.execute("SELECT * FROM well_contractors WHERE state = 'AZ' AND (data_freshness IS NULL OR data_freshness != 'enriched')")
    rows = c_m.fetchall()
    print(f"[*] Found {len(rows)} unenriched AZ records in master database.")
    
    if len(rows) == 0:
        print("[!] No unenriched AZ records found. Exiting.")
        return
        
    # Get columns
    columns = [col[0] for col in p3_schema.get_schema_columns()]
    placeholders = ", ".join(["?"] * len(columns))
    insert_query = f"INSERT INTO well_contractors ({', '.join(columns)}) VALUES ({placeholders})"
    
    inserted_ids = []
    
    # Insert well contractors and licenses
    for row in rows:
        old_id = row['id']
        val_list = []
        for col in columns:
            if col == 'id':
                val_list.append(None) # Auto-increment
            else:
                val_list.append(row[col])
        c_s.execute(insert_query, val_list)
        new_company_id = c_s.lastrowid
        inserted_ids.append((old_id, new_company_id))
        
        # Copy technician licenses
        c_m.execute("SELECT * FROM technician_licenses WHERE company_id = ?", (old_id,))
        lic_rows = c_m.fetchall()
        for lic in lic_rows:
            lic_cols = [col[0] for col in p3_schema.get_license_schema_columns()]
            lic_placeholders = ", ".join(["?"] * len(lic_cols))
            lic_insert = f"INSERT INTO technician_licenses ({', '.join(lic_cols)}) VALUES ({lic_placeholders})"
            
            lic_vals = []
            for col in lic_cols:
                if col == 'id':
                    lic_vals.append(None)
                elif col == 'company_id':
                    lic_vals.append(new_company_id)
                else:
                    lic_vals.append(lic[col])
            c_s.execute(lic_insert, lic_vals)
            
    conn_s.commit()
    
    # Mark the original master database records for deletion
    print("[*] Marking original records in Master DB with a deletion tag in listing_tier='marked_for_deletion'")
    c_m.execute("BEGIN TRANSACTION")
    for old_id, _ in inserted_ids:
        c_m.execute("UPDATE well_contractors SET listing_tier = 'marked_for_deletion' WHERE id = ?", (old_id,))
    conn_m.commit()
    
    conn_m.close()
    conn_s.close()
    
    print("[+] Isolated extraction and master deletion-marking complete.")

if __name__ == "__main__":
    main()
