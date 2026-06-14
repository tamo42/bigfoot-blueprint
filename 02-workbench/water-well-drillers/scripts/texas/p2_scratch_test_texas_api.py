import requests
import json
import os
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils

url = "https://data.texas.gov/resource/7358-krk7.json"

print("[*] Fetching sample 'Water Well Driller/Pump Installer' records from Texas Open Data Portal...")

params = {
    "license_type": "Water Well Driller/Pump Installer",
    "$limit": 5
}

# Resolve file output path relative to workspace root
output_path = utils.resolve_path("02-workbench/water-well-drillers/sample_texas_well_records.json")

try:
    response = requests.get(url, params=params, timeout=15)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        records = response.json()
        print(f"[+] Retrieved {len(records)} records.")
        if len(records) > 0:
            print(json.dumps(records, indent=2))
            
            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(records, f, indent=2)
            print(f"[+] Saved sample records to: {output_path}")
    else:
        print(f"[-] Error: {response.text[:500]}")
except Exception as e:
    print(f"[-] Error: {e}")
