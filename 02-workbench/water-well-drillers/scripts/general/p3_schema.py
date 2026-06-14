import sqlite3

def get_schema_columns():
    """
    Returns the core columns and types for the installers_haulers table.
    """
    columns = [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("post_status", "TEXT DEFAULT 'publish'"),
        ("name", "TEXT"),
        ("slug", "TEXT UNIQUE"),
        ("address", "TEXT"),
        ("city", "TEXT"),
        ("state", "TEXT"),
        ("zip_code", "TEXT"),
        ("county", "TEXT"),
        ("phone_number", "TEXT"),
        ("website_url", "TEXT"),
        ("claimed", "INTEGER DEFAULT 0"),
        ("google_rating", "REAL DEFAULT 0"),
        ("google_review_count", "INTEGER DEFAULT 0"),
        ("manual_lat", "REAL"),
        ("manual_lng", "REAL"),
        ("served_counties", "TEXT"),
        ("coi_status", "TEXT DEFAULT 'Unverified'"),
        ("pumper_certification_level", "TEXT"),
        ("listing_content", "TEXT"),
        ("fleet_size", "INTEGER"),
        ("fleet_registry_json", "TEXT"),
        ("google_place_id", "TEXT"),
        ("reviews_json", "TEXT")
    ]
    
    # Add 20 QA columns
    for i in range(1, 21):
        columns.append((f"qa_{i}_question", "TEXT"))
        columns.append((f"qa_{i}_answer", "TEXT"))
        
    # Add 3 individual review columns
    for i in range(1, 4):
        columns.append((f"review_{i}_text", "TEXT"))
        columns.append((f"review_{i}_author", "TEXT"))
        columns.append((f"review_{i}_rating", "REAL"))
        
    return columns

def initialize_database(db_path):
    """
    Creates and/or migrates the installers_haulers table in the SQLite database
    located at db_path to match the canonical schema.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if installers_haulers table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='installers_haulers'")
    exists = c.fetchone()
    
    columns = get_schema_columns()
    
    if not exists:
        # Create table from scratch
        col_defs = ", ".join([f"{col} {col_type}" for col, col_type in columns])
        c.execute(f"CREATE TABLE installers_haulers ({col_defs})")
        conn.commit()
        print(f"[+] Created installers_haulers table in: {db_path}")
    else:
        # Table exists. Let's inspect columns and add missing ones
        c.execute("PRAGMA table_info(installers_haulers)")
        existing_cols = {col_info[1].lower() for col_info in c.fetchall()}
        
        migrated = False
        for col_name, col_type in columns:
            if col_name.lower() not in existing_cols:
                # Alter table to add column
                # Since sqlite does not support altering multiple columns at once, we do them individually
                try:
                    c.execute(f"ALTER TABLE installers_haulers ADD COLUMN {col_name} {col_type}")
                    migrated = True
                except sqlite3.OperationalError as e:
                    print(f"  [-] Failed to add column {col_name}: {e}")
                    
        if migrated:
            conn.commit()
            print(f"[+] Migrated database schema for: {db_path}")
            
    conn.close()
