import json

with open(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\extracted_fog_ids.json", "r") as f:
    records = json.load(f)

for r in records:
    if "bowen" in r["company"].lower():
        print(r)
