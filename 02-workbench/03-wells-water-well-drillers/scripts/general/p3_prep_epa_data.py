import os
import csv
import json
from collections import defaultdict
from datetime import datetime

def parse_date_year(date_str):
    if not date_str:
        return 0
    try:
        # EPA dates often look like 'MM/DD/YYYY'
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        return dt.year
    except ValueError:
        # Fallback if it's 'DD-MON-YY' or similar
        try:
            return int(date_str[-4:])
        except ValueError:
            return 0

def prep_epa_data(epa_dir):
    systems_csv = os.path.join(epa_dir, "SDWA_PUB_WATER_SYSTEMS.csv")
    violations_csv = os.path.join(epa_dir, "SDWA_VIOLATIONS_ENFORCEMENT.csv")
    geo_csv = os.path.join(epa_dir, "SDWA_GEOGRAPHIC_AREAS.csv")
    ref_csv = os.path.join(epa_dir, "SDWA_REF_CODE_VALUES.csv")
    output_json = os.path.join(epa_dir, "epa_filtered_alerts.json")

    if not all(os.path.exists(f) for f in [systems_csv, violations_csv, geo_csv, ref_csv]):
        print("[!] Missing EPA bulk CSVs in cache/epa_sdwis/")
        return

    print("Building code maps...")
    code_map = {"CONTAMINANT_CODE": {}, "RULE_CODE": {}}
    with open(ref_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            val_type = row.get("VALUE_TYPE")
            if val_type in code_map:
                code_map[val_type][row.get("VALUE_CODE")] = row.get("VALUE_DESCRIPTION")

    print("Parsing PWS Systems (Groundwater only)...")
    system_info = {}
    with open(systems_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gw_sw_code = row.get("GW_SW_CODE", "")
            if gw_sw_code in ("GW", "GU"):
                pwsid = row.get("PWSID")
                system_info[pwsid] = {
                    "name": row.get("PWS_NAME", "Unknown System"),
                    "population": int(row.get("POPULATION_SERVED_COUNT", 0) or 0),
                    "state": "",
                    "county": "",
                    "violations": []
                }

    print("Mapping Geographic Areas...")
    with open(geo_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pwsid = row.get("PWSID")
            if pwsid in system_info:
                state = row.get("STATE_SERVED", "")
                county = row.get("COUNTY_SERVED", "")
                clean_county = county.replace("County", "").replace("county", "").strip().lower()
                system_info[pwsid]["state"] = state.lower()
                if clean_county:
                    system_info[pwsid]["county"] = clean_county

    print("Filtering Violations (Last 5 years, Health-based)...")
    current_year = datetime.now().year
    with open(violations_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pwsid = row.get("PWSID")
            is_health_based = row.get("IS_HEALTH_BASED_IND", "N")
            
            if pwsid in system_info and is_health_based == 'Y':
                date_str = row.get("COMPL_PER_BEGIN_DATE", "")
                year = parse_date_year(date_str)
                
                # Filter for last 5 years
                if year >= (current_year - 5):
                    contam_code = row.get("CONTAMINANT_CODE", "")
                    rule_code = row.get("RULE_CODE", "")
                    
                    contaminant = code_map["CONTAMINANT_CODE"].get(contam_code, f"Code {contam_code}")
                    rule = code_map["RULE_CODE"].get(rule_code, f"Rule {rule_code}")
                    
                    system_info[pwsid]["violations"].append({
                        "date": date_str,
                        "contaminant": contaminant,
                        "rule": rule,
                        "is_major": row.get("IS_MAJOR_VIOL_IND", "N")
                    })

    print("Building local JSON repository...")
    lookup = defaultdict(list)
    for pwsid, info in system_info.items():
        if len(info["violations"]) > 0 and info["state"] and info["county"]:
            key = f'{info["state"]}_{info["county"]}'.lower()
            
            # Sort violations by date descending (newest first) and keep top 5
            # We use a simple sort by year extracted, or just keep it naive if dates are messy
            def get_sort_key(v):
                return parse_date_year(v["date"])
            
            sorted_violations = sorted(info["violations"], key=get_sort_key, reverse=True)[:5]
            
            lookup[key].append({
                "system_name": info["name"],
                "total_health_violations_last_5_years": len(info["violations"]),
                "recent_violations": sorted_violations,
                "population_served": info["population"]
            })

    # Sort systems in each county by population size and keep top 5
    for key in lookup:
        lookup[key] = sorted(lookup[key], key=lambda x: x["population_served"], reverse=True)[:5]

    print(f"Writing {output_json}...")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(lookup, f, indent=2)
    
    print("Pre-processing complete! You can now run p3_enrich_epa.py instantly.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    epa_dir = os.path.join(base_dir, "cache", "epa_sdwis")
    prep_epa_data(epa_dir)
