import os
import sqlite3
import argparse
import sys

def get_workspace_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))

def append_state_database(state_db_path, master_db_path):
    if not os.path.exists(state_db_path):
        print(f"[-] State database not found: {state_db_path}")
        sys.exit(1)
    if not os.path.exists(master_db_path):
        print(f"[-] Master database not found: {master_db_path}")
        sys.exit(1)
        
    print(f"[*] Attaching state database: {state_db_path}")
    print(f"[*] Target master database: {master_db_path}")
    
    conn_master = sqlite3.connect(master_db_path)
    conn_master.row_factory = sqlite3.Row
    c_master = conn_master.cursor()
    
    conn_state = sqlite3.connect(state_db_path)
    conn_state.row_factory = sqlite3.Row
    c_state = conn_state.cursor()
    
    # 1. Inspect table schemas
    c_state.execute("PRAGMA table_info(well_contractors)")
    state_cols = [col[1] for col in c_state.fetchall()]
    
    c_master.execute("PRAGMA table_info(well_contractors)")
    master_cols = [col[1] for col in c_master.fetchall()]
    
    # Identify intersection of columns to copy (excluding auto-increment ID)
    common_cols = [col for col in state_cols if col in master_cols and col.lower() != 'id']
    print(f"[*] Common columns to append: {common_cols}")
    
    # 2. Get all contractors from the state database
    c_state.execute("SELECT * FROM well_contractors")
    state_contractors = c_state.fetchall()
    print(f"[*] Found {len(state_contractors)} records in the state database.")
    
    appended_companies = 0
    skipped_companies = 0
    appended_licenses = 0
    
    try:
        c_master.execute("BEGIN TRANSACTION")
        
        # Clean up records marked for deletion to prevent duplicate slug conflicts
        c_master.execute("SELECT id FROM well_contractors WHERE listing_tier = 'marked_for_deletion'")
        marked_ids = [r[0] for r in c_master.fetchall()]
        if marked_ids:
            print(f"[*] Found {len(marked_ids)} records marked for deletion in master DB. Cleaning them up...")
            # Delete child licenses first
            placeholders = ", ".join(["?"] * len(marked_ids))
            c_master.execute(f"DELETE FROM technician_licenses WHERE company_id IN ({placeholders})", marked_ids)
            c_master.execute(f"DELETE FROM well_contractors WHERE id IN ({placeholders})", marked_ids)
            print(f"[+] Cleaned up marked records and matching child licenses.")
            
        for comp in state_contractors:
            slug = comp['slug']
            old_id = comp['id']
            
            # Check if this slug already exists in the master database
            c_master.execute("SELECT id FROM well_contractors WHERE slug = ?", (slug,))
            exists = c_master.fetchone()
            
            if exists:
                print(f"  [-] Skipping company '{comp['name']}' (slug '{slug}' already exists in master).")
                skipped_companies += 1
                continue
                
            # Prepare values for insertion
            placeholders = ", ".join(["?"] * len(common_cols))
            insert_query = f"INSERT INTO well_contractors ({', '.join(common_cols)}) VALUES ({placeholders})"
            values = [comp[col] for col in common_cols]
            
            c_master.execute(insert_query, values)
            new_company_id = c_master.lastrowid
            appended_companies += 1
            
            # 3. Retrieve and copy associated technician licenses
            c_state.execute("SELECT * FROM technician_licenses WHERE company_id = ?", (old_id,))
            licenses = c_state.fetchall()
            
            for lic in licenses:
                # Get columns for license table (excluding id and company_id)
                c_state.execute("PRAGMA table_info(technician_licenses)")
                lic_cols = [col[1] for col in c_state.fetchall()]
                
                common_lic_cols = [col for col in lic_cols if col.lower() not in ('id', 'company_id')]
                
                lic_placeholders = ", ".join(["?"] * (len(common_lic_cols) + 1))
                insert_lic_query = f"""
                    INSERT INTO technician_licenses (company_id, {', '.join(common_lic_cols)}) 
                    VALUES ({lic_placeholders})
                """
                
                lic_values = [new_company_id] + [lic[col] for col in common_lic_cols]
                c_master.execute(insert_lic_query, lic_values)
                appended_licenses += 1
                
        c_master.execute("COMMIT")
        print(f"\n[+] Relational append completed successfully:")
        print(f"    - Companies appended: {appended_companies}")
        print(f"    - Companies skipped (duplicates): {skipped_companies}")
        print(f"    - Licenses appended and mapped: {appended_licenses}")
        
    except Exception as e:
        c_master.execute("ROLLBACK")
        print(f"[-] Append failed: {e}")
        raise e
    finally:
        conn_master.close()
        conn_state.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Relational append of an enriched state database to the master database.")
    parser.add_argument("--state-db", help="Path to local enriched state database sqlite file.")
    parser.add_argument("--master-db", help="Path to master directory.sqlite database file.")
    
    args = parser.parse_args()
    
    workspace = get_workspace_root()
    
    state_db = args.state_db
    if not state_db:
        # Default fallback (e.g. florida_wells.sqlite)
        state_db = os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "data", "florida_wells.sqlite")
        
    master_db = args.master_db
    if not master_db:
        master_db = os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "data", "water_well_directory.sqlite")
        
    append_state_database(state_db, master_db)
