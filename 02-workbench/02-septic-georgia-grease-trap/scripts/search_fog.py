import json

with open(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\extracted_fog_ids.json", "r") as f:
    records = json.load(f)

def find_matches(query):
    print(f"\n--- Matches for query: '{query}' ---")
    q = query.lower()
    for r in records:
        if q in r["company"].lower() or q in r["city"].lower() or q in r["phone_tag"].replace(" ", "").replace("-", "").replace("(", "").replace(")", ""):
            print(f"Company: {r['company']} | City: {r['city']} | Phone: {r['phone_tag']} | FOG ID: {r['fog_id']}")

find_matches("bowen")
find_matches("ricky")
find_matches("safety")
find_matches("ameripro")
find_matches("remedies")
find_matches("environmental")
find_matches("478")
find_matches("a-1")
find_matches("a1")
