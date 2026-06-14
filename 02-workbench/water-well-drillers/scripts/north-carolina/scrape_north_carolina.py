import os
import sys
import csv
import sqlite3
import json

# Add scripts/general to path to import utils and schema
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'general'))
import schema
import utils

def main():
    db_path = utils.get_db_path("north_carolina")
    schema.initialize_database(db_path)
    
    csv_file = os.path.join(os.path.dirname(__file__), "Current_Certified_Drillers_List.csv")
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)
        
    companies = {}
    
    with open(csv_file, mode='r', encoding='windows-1252') as f:
        # handle potential BOM or windows encoding
        reader = csv.DictReader(f)
        
        for row in reader:
            employer = row.get('Employer', '').strip()
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            
            # Use employee name if employer is blank
            company_name = employer if employer else f"{first_name} {last_name}"
            company_name = company_name.strip()
            
            if not company_name:
                continue
                
            if company_name not in companies:
                companies[company_name] = {
                    'name': company_name,
                    'state': row.get('Employer State', '').strip(),
                    'county': row.get('Employer County', '').strip(),
                    'phone_number': utils.clean_phone_number(row.get('Employer Phone', '').strip()),
                    'personnel': [],
                    'services': set()
                }
                
            # Compile personnel info
            cert = row.get('Cert .', row.get('Cert', '')).strip()
            level = row.get('Level', '').strip()
            personnel_str = f"{first_name} {last_name}"
            if cert or level:
                details = []
                if cert: details.append(f"Cert: {cert}")
                if level: details.append(f"Level: {level}")
                personnel_str += f" ({', '.join(details)})"
            
            companies[company_name]['personnel'].append(personnel_str)
            
            # Aggregate services
            service_cols = [
                'Well Construction', 'Environmental', 'Geothermal', 'Irrigation Well',
                'Refracturing', 'Well Abandonment or Repair', 'Pump Install/Repair', 'Down Hole Camera'
            ]
            for col in service_cols:
                if row.get(col, '').strip().lower() == 'yes':
                    companies[company_name]['services'].add(col)

    print(f"Aggregated {len(companies)} unique companies from the CSV.")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    inserted = 0
    updated = 0
    
    for company_name, data in companies.items():
        slug = utils.slugify(f"{company_name} {data['state']}")
        
        # Format listing content
        content_lines = ["**Certified Personnel:**"]
        for p in data['personnel']:
            content_lines.append(f"- {p}")
            
        if data['services']:
            content_lines.append("\n**Authorized Services:**")
            for s in sorted(data['services']):
                content_lines.append(f"- {s}")
                
        listing_content = "\n".join(content_lines)
        
        # Check if slug exists
        c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (slug,))
        row = c.fetchone()
        
        if row:
            # Update existing
            c.execute("""
                UPDATE installers_haulers
                SET name = ?, county = ?, state = ?, phone_number = ?, listing_content = ?
                WHERE id = ?
            """, (data['name'], data['county'], data['state'], data['phone_number'], listing_content, row[0]))
            updated += 1
        else:
            # Insert new
            c.execute("""
                INSERT INTO installers_haulers 
                (name, slug, county, state, phone_number, listing_content)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['name'], slug, data['county'], data['state'], data['phone_number'], listing_content))
            inserted += 1
            
    conn.commit()
    conn.close()
    
    print(f"Done! Inserted: {inserted}, Updated: {updated}")

if __name__ == '__main__':
    main()
