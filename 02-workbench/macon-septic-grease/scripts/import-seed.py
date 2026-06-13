import os
import csv
import sqlite3
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    db_file = data_dir / "directory.sqlite"
    csv_file = data_dir / "septic-grease-seed.csv"
    
    if not csv_file.exists():
        print(f"Error: Seed CSV file '{csv_file.name}' not found. Run fetch-seed.py first.")
        return
        
    print(f"Bootstrapping database: {db_file.name}...")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Initialize schema as described in architect-schema.md
    c.execute("""
    CREATE TABLE IF NOT EXISTS installers_haulers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        place_id TEXT UNIQUE,
        address TEXT,
        city TEXT DEFAULT 'Macon',
        state TEXT DEFAULT 'GA',
        zip_code TEXT,
        phone TEXT,
        website_url TEXT,
        latitude REAL,
        longitude REAL,
        google_rating REAL DEFAULT 0.0,
        google_review_count INTEGER DEFAULT 0,
        reviews_json TEXT DEFAULT '[]',
        license_no TEXT,
        license_status TEXT DEFAULT 'Unverified',
        permit_expiration TEXT,
        specialty_grease_trap INTEGER DEFAULT 0,
        specialty_septic_pump INTEGER DEFAULT 0,
        specialty_riser_install INTEGER DEFAULT 0,
        specialty_line_jetting INTEGER DEFAULT 0,
        specialty_inspections INTEGER DEFAULT 0,
        specialty_emergency_dispatch INTEGER DEFAULT 0,
        specialties_crawled INTEGER DEFAULT 0,
        profile_bio TEXT,
        faq_json TEXT DEFAULT '[]',
        speakable_bio TEXT,
        claimed INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    
    print("Reading seed CSV and importing records...")
    import_count = 0
    duplicate_count = 0
    
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                c.execute("""
                INSERT INTO installers_haulers (
                    name, place_id, address, city, state, zip_code, 
                    latitude, longitude, google_rating, google_review_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["name"],
                    row["place_id"],
                    row["address"],
                    row["city"],
                    row["state"],
                    row["zip_code"],
                    float(row["latitude"]) if row["latitude"] else None,
                    float(row["longitude"]) if row["longitude"] else None,
                    float(row["google_rating"]) if row["google_rating"] else 0.0,
                    int(row["google_review_count"]) if row["google_review_count"] else 0
                ))
                import_count += 1
            except sqlite3.IntegrityError:
                # Deduplication fallback if place_id matches
                duplicate_count += 1
                
    conn.commit()
    conn.close()
    
    print(f"\nImport Complete!")
    print(f"  - Imported: {import_count} records")
    print(f"  - Skipped duplicates: {duplicate_count} records")

if __name__ == "__main__":
    main()
