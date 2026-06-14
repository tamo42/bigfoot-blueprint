import json

with open(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\extracted_fog_ids.json", "r") as f:
    records = json.load(f)

for r in records:
    if "ricky heath" in r["company"].lower():
        print(r)
