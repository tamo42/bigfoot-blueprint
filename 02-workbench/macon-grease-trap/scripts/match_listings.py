import sqlite3
import json
import difflib

def clean_name(name):
    # Strip common suffixes and punctuation to improve matching
    n = name.lower()
    for word in ['llc', 'inc', 'co', 'corp', 'services', 'service', 'company', 'and', '&', ',', '.', '-']:
        n = n.replace(word, ' ')
    return ' '.join(n.split())

def main():
    # Load listings from DB
    db_path = r"c:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, name FROM installers_haulers")
    db_listings = c.fetchall()
    conn.close()

    # Load FOG data
    fog_path = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\extracted_fog_ids.json"
    with open(fog_path, 'r') as f:
        fog_records = json.load(f)

    # Group FOG records by unique company
    fog_companies = {}
    for r in fog_records:
        comp = r["company"]
        if comp not in fog_companies:
            fog_companies[comp] = []
        fog_companies[comp].append(r)

    print("--- Listing Matches ---")
    for db_id, db_name in db_listings:
        db_clean = clean_name(db_name)
        best_ratio = 0
        best_match = None
        
        for fog_comp, records in fog_companies.items():
            fog_clean = clean_name(fog_comp)
            # Check ratio
            ratio = difflib.SequenceMatcher(None, db_clean, fog_clean).ratio()
            # Also check if one is a substring of another
            if db_clean in fog_clean or fog_clean in db_clean:
                ratio = max(ratio, 0.8)
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = (fog_comp, records)
        
        if best_ratio > 0.5:
            print(f"\nDB: {db_name} (ID: {db_id})")
            print(f"  Best Match: {best_match[0]} (Ratio: {best_ratio:.2f})")
            for r in best_match[1]:
                print(f"    FOG ID: {r['fog_id']} | City: {r['city']} | Phone: {r['phone_tag']}")
        else:
            print(f"\nDB: {db_name} (ID: {db_id}) -> No close match")

if __name__ == '__main__':
    main()
