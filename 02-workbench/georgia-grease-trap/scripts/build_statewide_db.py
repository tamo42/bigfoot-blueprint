import json
import sqlite3
import re
import os
from collections import defaultdict

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]+', '', text)
    text = re.sub(r'\-\-+', '-', text)
    return text.strip('-')

input_file = r'C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\extracted_fog_ids.json'
output_db = r'C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite'
pending_json = r'C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\pending_enrichment.json'

with open(input_file, 'r') as f:
    data = json.load(f)

# Group by company
companies = defaultdict(lambda: {
    "city": "", "state": "", "zip": "", "phone": "", "trucks": []
})

for row in data:
    company = row.get("company", "").strip()
    if not company:
        continue
    
    # Parse phone_tag: "(205) 252-1197 AL-1212359" or "706-555-1234 TAG"
    pt = row.get("phone_tag", "")
    phone_match = re.search(r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', pt)
    phone = phone_match.group(0) if phone_match else ""
    
    # The rest is the truck tag
    truck_tag = pt.replace(phone, "").strip() if phone else pt.strip()
    
    c_data = companies[company]
    # Update baseline info (take the last non-empty one)
    if row.get("city"): c_data["city"] = row.get("city").strip()
    if row.get("state"): c_data["state"] = row.get("state").strip()
    if row.get("zip"): c_data["zip"] = str(row.get("zip")).strip()
    if phone: c_data["phone"] = phone
    
    c_data["trucks"].append({
        "truck_tag": truck_tag,
        "fog_id": row.get("fog_id", "").strip()
    })

# Deduplicate slugs
slug_counts = {}
final_records = []
for company_name, c_data in companies.items():
    base_slug = slugify(company_name)
    slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
    
    slug = base_slug
    if slug_counts[base_slug] > 1:
        slug = f"{base_slug}-{slugify(c_data['city'])}"
        
    final_records.append({
        "name": company_name,
        "slug": slug,
        "city": c_data["city"],
        "state": c_data["state"],
        "zip_code": c_data["zip"],
        "phone_number": c_data["phone"],
        "fleet_size": len(c_data["trucks"]),
        "fleet_registry_json": json.dumps(c_data["trucks"])
    })

print(f"Processed {len(final_records)} unique companies.")

# Let's save the final records to pending_enrichment.json so the agent can loop through them
with open(pending_json, 'w') as f:
    json.dump(final_records, f, indent=2)

print("Saved pending_enrichment.json for LLM processing.")

# Now create/update the SQLite database
os.makedirs(os.path.dirname(output_db), exist_ok=True)
conn = sqlite3.connect(output_db)
c = conn.cursor()

# We will create a new table schema that matches what Astro expects, plus the new columns
c.execute('''
    CREATE TABLE IF NOT EXISTS installers_haulers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_status TEXT DEFAULT 'publish',
        name TEXT,
        slug TEXT UNIQUE,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        county TEXT,
        phone_number TEXT,
        website_url TEXT,
        claimed INTEGER DEFAULT 0,
        google_rating REAL DEFAULT 0,
        google_review_count INTEGER DEFAULT 0,
        manual_lat REAL,
        manual_lng REAL,
        served_counties TEXT,
        mwa_fog_compliance_code TEXT,
        coi_status TEXT,
        eo_insurance_limit TEXT,
        pumper_certification_level TEXT,
        line_jetting_available TEXT,
        quickfact_best_for TEXT,
        quickfact_primary_items TEXT,
        quickfact_fee_structure TEXT,
        quickfact_access TEXT,
        listing_content TEXT,
        fleet_size INTEGER,
        fleet_registry_json TEXT
    )
''')

# Also add the qa_x_question columns dynamically
for i in range(1, 21):
    try:
        c.execute(f'ALTER TABLE installers_haulers ADD COLUMN qa_{i}_question TEXT')
        c.execute(f'ALTER TABLE installers_haulers ADD COLUMN qa_{i}_answer TEXT')
    except sqlite3.OperationalError:
        pass # Column already exists
        
# Add review_x_text columns
for i in range(1, 4):
    try:
        c.execute(f'ALTER TABLE installers_haulers ADD COLUMN review_{i}_text TEXT')
        c.execute(f'ALTER TABLE installers_haulers ADD COLUMN review_{i}_author TEXT')
    except sqlite3.OperationalError:
        pass

# Ensure fleet_size, fleet_registry_json, and slug exist if table was already created
try:
    c.execute('ALTER TABLE installers_haulers ADD COLUMN slug TEXT')
except sqlite3.OperationalError:
    pass

try:
    c.execute('ALTER TABLE installers_haulers ADD COLUMN fleet_size INTEGER')
    c.execute('ALTER TABLE installers_haulers ADD COLUMN fleet_registry_json TEXT')
except sqlite3.OperationalError:
    pass

# Insert the records (ignore duplicates for now, or update)
for rec in final_records:
    # Basic address approximation
    address = f"{rec['city']}, {rec['state']} {rec['zip_code']}"
    
    c.execute('''
        INSERT OR IGNORE INTO installers_haulers 
        (name, slug, address, city, state, zip_code, phone_number, fleet_size, fleet_registry_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        rec['name'], rec['slug'], address, rec['city'], rec['state'], rec['zip_code'], 
        rec['phone_number'], rec['fleet_size'], rec['fleet_registry_json']
    ))
    
    # If the record already exists, update its fleet details
    c.execute('''
        UPDATE installers_haulers SET 
            fleet_size = ?,
            fleet_registry_json = ?,
            city = ?,
            state = ?,
            zip_code = ?,
            phone_number = ?
        WHERE slug = ?
    ''', (
        rec['fleet_size'], rec['fleet_registry_json'], rec['city'], rec['state'], rec['zip_code'], rec['phone_number'], rec['slug']
    ))

conn.commit()
conn.close()

print(f"Successfully populated {output_db}")
