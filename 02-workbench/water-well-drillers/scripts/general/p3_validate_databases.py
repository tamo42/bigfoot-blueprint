import os
import sqlite3
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import p3_utils as utils
import p3_schema as schema

def get_db_columns(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(well_contractors)")
    cols = {row[1]: row[2] for row in c.fetchall()}
    conn.close()
    return cols

def main():
    data_dir = utils.resolve_path("02-workbench/water-well-drillers/data")
    db_files = [f for f in os.listdir(data_dir) if f.endswith(".sqlite")]
    db_paths = {f.split(".")[0]: os.path.join(data_dir, f) for f in db_files}

    
    print("[*] Validating SQLite database files schema symmetry...")
    
    # First, run initialization to make sure all columns are migrated/present
    for state, path in db_paths.items():
        if not os.path.exists(path):
            print(f"[-] Error: Database for {state} does not exist at: {path}")
            continue
        print(f"[*] Ensuring canonical schema is applied to: {state}")
        schema.initialize_database(path)
        
    print("\n[*] Comparing table schemas...")
    reference_cols = None
    reference_state = None
    
    errors = 0
    for state, path in db_paths.items():
        if not os.path.exists(path):
            continue
            
        try:
            cols = get_db_columns(path)
            print(f"  [+] {state.title()} database column count: {len(cols)}")
            
            if reference_cols is None:
                reference_cols = cols
                reference_state = state
            else:
                # Compare columns
                ref_keys = set(reference_cols.keys())
                state_keys = set(cols.keys())
                
                missing_in_state = ref_keys - state_keys
                extra_in_state = state_keys - ref_keys
                
                if missing_in_state:
                    print(f"  [-] Schema mismatch in {state.title()}: missing columns {missing_in_state}")
                    errors += 1
                if extra_in_state:
                    print(f"  [-] Schema mismatch in {state.title()}: extra columns {extra_in_state}")
                    errors += 1
                    
                # Compare types
                for col in ref_keys & state_keys:
                    if reference_cols[col] != cols[col]:
                        print(f"  [-] Type mismatch for {col} in {state.title()}: expected {reference_cols[col]} but got {cols[col]}")
                        errors += 1
        except Exception as e:
            print(f"  [-] Failed to inspect database for {state}: {e}")
            errors += 1
            
    if errors == 0:
        print("\n[+] SUCCESS: All database schemas are symmetric and aligned with the canonical definition!")
        sys.exit(0)
    else:
        print(f"\n[-] FAILED: Detected {errors} schema mismatches between state databases.")
        sys.exit(1)

if __name__ == "__main__":
    main()
