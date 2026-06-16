import json

# Middle Georgia cities
middle_ga_cities = [
    "macon", "warner robins", "perry", "centerville", 
    "fort valley", "byron", "gray", "forsyth", 
    "milledgeville", "roberta", "jeffersonville", "irwinton",
    "dublin", "east dublin", "cochran", "jackson", "gray"
]

with open(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\extracted_fog_ids.json", "r") as f:
    records = json.load(f)

print("=== Middle Georgia Registered Transporters ===")
found_companies = {}
for r in records:
    city = r["city"].lower().strip()
    match = False
    for target in middle_ga_cities:
        if target in city:
            match = True
            break
            
    if match:
        comp = r["company"]
        if comp not in found_companies:
            found_companies[comp] = []
        found_companies[comp].append(r)

print(f"{'Company Name':<45} | {'City':<15} | {'FOG IDs'}")
print("-" * 80)
for comp, recs in sorted(found_companies.items()):
    cities = list(set(r["city"] for r in recs))
    fog_ids = [r["fog_id"] for r in recs]
    print(f"{comp:<45} | {', '.join(cities):<15} | {', '.join(fog_ids)}")
