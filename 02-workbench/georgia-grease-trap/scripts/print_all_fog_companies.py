import json

with open(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\extracted_fog_ids.json", "r") as f:
    records = json.load(f)

# Group by company
companies = {}
for r in records:
    c = r["company"]
    if c not in companies:
        companies[c] = []
    companies[c].append(r)

print(f"{'Company Name':<45} | {'City':<15} | {'Phone':<15} | {'FOG IDs'}")
print("-" * 100)
for c, recs in sorted(companies.items()):
    cities = list(set(r["city"] for r in recs))
    phones = list(set(r["phone_tag"] for r in recs))
    fog_ids = [r["fog_id"] for r in recs]
    print(f"{c:<45} | {', '.join(cities):<15} | {recs[0]['phone_tag']:<15} | {', '.join(fog_ids)}")
