import json

fog_path = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\extracted_fog_ids.json"
with open(fog_path, 'r') as f:
    records = json.load(f)

search_terms = ["bowen", "heath", "safety", "ameripro", "pumping", "remedies", "environmental"]

for term in search_terms:
    print(f"\n=== Search results for: {term} ===")
    found = False
    for r in records:
        if term in r["company"].lower():
            print(f"Company: {r['company']}")
            print(f"  FOG ID: {r['fog_id']}")
            print(f"  City/State/Zip: {r['city']}, {r['state']} {r['zip']}")
            print(f"  Phone Tag: {r['phone_tag']}")
            print(f"  Page: {r['page']}")
            found = True
    if not found:
        print("No matches")
