import os
import sqlite3
import csv

def main():
    print("=========================================================")
    print("Georgia Closing Attorneys - SQLite Database Importer")
    print("=========================================================")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), "data", "georgia-closing-attorneys_seed.csv")
    db_path = os.path.join(os.path.dirname(current_dir), "data", "directory.sqlite")
    
    if not os.path.exists(csv_path):
        print(f"Error: Seed CSV file not found at {csv_path}")
        return
        
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create attorneys table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attorneys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gabar_id TEXT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        bar_number TEXT UNIQUE,
        license_status TEXT,
        admission_date TEXT,
        disciplinary_history TEXT DEFAULT 'None',
        firm_name TEXT,
        office_address TEXT,
        city TEXT,
        county TEXT,
        zip_code TEXT,
        latitude REAL,
        longitude REAL,
        phone TEXT,
        email TEXT,
        website_url TEXT,
        coi_verified INTEGER DEFAULT 0,
        coi_limits TEXT,
        appointments TEXT,
        specialties TEXT,
        listing_content TEXT,
        speakable_what_you_find TEXT,
        speakable_listing_details TEXT,
        speakable_quick_facts TEXT,
        quickfact_best_for TEXT,
        quickfact_primary_items TEXT,
        quickfact_fee_structure TEXT,
        quickfact_access TEXT,
        faq_enriched TEXT,
        claimed INTEGER DEFAULT 0
    )
    """)
    
    # Read CSV and insert records
    print("Reading seed CSV and importing to SQLite...")
    inserted_count = 0
    skipped_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gabar_id = row.get('id', '').strip()
            bar_number = row.get('bar_number', '').strip()
            
            if not bar_number:
                skipped_count += 1
                continue
                
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            license_status = row.get('status', '').strip()
            admission_date = row.get('admit_date', '').strip()
            firm_name = row.get('company', '').strip()
            
            # Construct address
            addr1 = row.get('address1', '').strip()
            addr2 = row.get('address2', '').strip()
            office_address = addr1
            if addr2:
                office_address = f"{addr1}, {addr2}" if addr1 else addr2
                
            city = row.get('city', '').strip()
            county = row.get('county', '').strip()
            zip_code = row.get('zip', '').strip()
            phone = row.get('phone', '').strip()
            email = row.get('email', '').strip()
            
            try:
                cursor.execute("""
                INSERT INTO attorneys (
                    gabar_id, first_name, last_name, bar_number, license_status, 
                    admission_date, firm_name, office_address, city, county, 
                    zip_code, phone, email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bar_number) DO UPDATE SET
                    gabar_id = excluded.gabar_id,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    license_status = excluded.license_status,
                    admission_date = excluded.admission_date,
                    firm_name = excluded.firm_name,
                    office_address = excluded.office_address,
                    city = excluded.city,
                    county = excluded.county,
                    zip_code = excluded.zip_code,
                    phone = excluded.phone,
                    email = excluded.email
                """, (
                    gabar_id, first_name, last_name, bar_number, license_status,
                    admission_date, firm_name, office_address, city, county,
                    zip_code, phone, email
                ))
                inserted_count += 1
            except Exception as e:
                print(f"Error importing bar number {bar_number}: {e}")
                skipped_count += 1
                
    conn.commit()
    conn.close()
    
    print("\nImport completed successfully.")
    print(f"Total rows processed: {inserted_count + skipped_count}")
    print(f"Records imported/updated: {inserted_count}")
    print(f"Records skipped: {skipped_count}")

if __name__ == "__main__":
    main()
