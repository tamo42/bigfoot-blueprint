import sqlite3

def get_schema_columns():
    """
    Returns the core columns and types for the well_contractors table.
    """
    columns = [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        # Layer 1 & 2: Core Location, Contact & Import Requirements
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
        ("featured", "INTEGER DEFAULT 0"),
        ("admin_category", "TEXT"),
        ("admin_location", "TEXT"),
        ("listing_img", "TEXT"),
        ("date", "TEXT"),

        # Layer 3: Domain-Specific Fields (21 Fields - remaining 4 moved to technician_licenses)
        ("emergency_repair_247", "INTEGER DEFAULT 0"),
        ("emergency_response_time", "TEXT"),
        ("emergency_services_offered", "TEXT"),
        ("service_radius_miles", "INTEGER"),
        ("served_counties", "TEXT"),
        ("drilling_depth_limit", "TEXT"),
        ("drilling_methods_available", "TEXT"),
        ("drilling_diameters", "TEXT"),
        ("geological_specialties", "TEXT"),
        ("well_rehabilitation_offered", "TEXT"),
        ("pump_types_serviced", "TEXT"),
        ("pump_brands_serviced", "TEXT"),
        ("pressure_tank_services", "INTEGER DEFAULT 0"),
        ("water_testing_offered", "INTEGER DEFAULT 0"),
        ("water_contaminants_tested", "TEXT"),
        ("water_treatment_installed", "TEXT"),
        ("residential_capable", "INTEGER DEFAULT 0"),
        ("commercial_capable", "INTEGER DEFAULT 0"),
        ("bonded_insured_details", "TEXT"),
        ("payment_methods_accepted", "TEXT"),
        ("financing_available", "INTEGER DEFAULT 0"),
        ("accepts_usda_rural_grants", "INTEGER DEFAULT 0"),
        ("handles_new_permits", "INTEGER DEFAULT 0"),
        ("wells_drilled_last_5_years", "INTEGER"),
        ("average_well_depth_ft", "INTEGER"),
        ("average_yield_gpm", "INTEGER"),
        ("local_epa_water_alerts", "TEXT"),
        ("local_groundwater_conditions", "TEXT"),


        # Layer 4: AI Enrichment Layer (Descriptions, Speakables, Quick Facts)
        ("listing_content", "TEXT"),
        ("speakable_what_you_find", "TEXT"),
        ("speakable_listing_details", "TEXT"),
        ("speakable_quick_facts", "TEXT"),
        ("quickfact_best_for", "TEXT"),
        ("quickfact_primary_services", "TEXT"),
        ("quickfact_pricing_guide", "TEXT"),
        ("quickfact_service_area", "TEXT"),

        # Layer 5: Google Places Integration
        ("google_place_id", "TEXT"),
        ("google_rating", "REAL DEFAULT 0"),
        ("google_review_count", "INTEGER DEFAULT 0"),
        ("manual_lat", "REAL"),
        ("manual_lng", "REAL"),
        ("reviews_json", "TEXT"),

        # Layer 6: Data Freshness & Source Tracking
        ("data_freshness", "TEXT"),
        ("enriched_at", "TEXT"),
        ("enrichment_source", "TEXT"),
        ("data_source", "TEXT"),
        ("source_id", "TEXT"),

        # Layer 7: Monetization Fields
        ("listing_tier", "TEXT DEFAULT 'free'"),
        ("advertiser_cta_url", "TEXT"),
        ("affiliate_hook_category", "TEXT"),
        ("email_optin_hook", "TEXT"),
    ]
    
    # Add 10 QA columns (20 fields in total)
    for i in range(1, 11):
        columns.append((f"qa_{i}_question", "TEXT"))
        columns.append((f"qa_{i}_answer", "TEXT"))
        
    # Add 3 individual review columns
    for i in range(1, 4):
        columns.append((f"review_{i}_text", "TEXT"))
        columns.append((f"review_{i}_author", "TEXT"))
        columns.append((f"review_{i}_rating", "REAL"))
        
    return columns

def get_license_schema_columns():
    """
    Returns the columns and types for the technician_licenses table.
    """
    return [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("company_id", "INTEGER"),
        ("license_holder", "TEXT"),
        ("license_number", "TEXT"),
        ("license_type", "TEXT"),
        ("license_status", "TEXT"),
        ("licensing_agency", "TEXT")
    ]

def initialize_database(db_path):
    """
    Creates and/or migrates both tables in the SQLite database at db_path
    to match the canonical relational schema.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Initialize parent table (well_contractors)
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='well_contractors'")
    exists_parent = c.fetchone()
    parent_columns = get_schema_columns()
    
    if not exists_parent:
        col_defs = ", ".join([f"{col} {col_type}" for col, col_type in parent_columns])
        c.execute(f"CREATE TABLE well_contractors ({col_defs})")
        print(f"[+] Created well_contractors table in: {db_path}")
    else:
        # Table exists. Migrate columns incrementally if needed
        c.execute("PRAGMA table_info(well_contractors)")
        existing_cols = {col_info[1].lower() for col_info in c.fetchall()}
        migrated = False
        for col_name, col_type in parent_columns:
            if col_name.lower() not in existing_cols:
                try:
                    c.execute(f"ALTER TABLE well_contractors ADD COLUMN {col_name} {col_type}")
                    migrated = True
                except sqlite3.OperationalError as e:
                    print(f"  [-] Failed to add column {col_name} to well_contractors: {e}")
        if migrated:
            print(f"[+] Migrated well_contractors schema in: {db_path}")

    # 2. Initialize child table (technician_licenses)
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='technician_licenses'")
    exists_child = c.fetchone()
    child_columns = get_license_schema_columns()
    
    if not exists_child:
        col_defs = ", ".join([f"{col} {col_type}" for col, col_type in child_columns])
        # Add foreign key constraint
        fk_constraint = ", FOREIGN KEY(company_id) REFERENCES well_contractors(id) ON DELETE CASCADE"
        c.execute(f"CREATE TABLE technician_licenses ({col_defs}{fk_constraint})")
        print(f"[+] Created technician_licenses table in: {db_path}")
    else:
        # Table exists. Migrate columns incrementally if needed
        c.execute("PRAGMA table_info(technician_licenses)")
        existing_cols = {col_info[1].lower() for col_info in c.fetchall()}
        migrated = False
        for col_name, col_type in child_columns:
            if col_name.lower() not in existing_cols:
                try:
                    c.execute(f"ALTER TABLE technician_licenses ADD COLUMN {col_name} {col_type}")
                    migrated = True
                except sqlite3.OperationalError as e:
                    print(f"  [-] Failed to add column {col_name} to technician_licenses: {e}")
        if migrated:
            print(f"[+] Migrated technician_licenses schema in: {db_path}")
            
    conn.commit()
    conn.close()
