import sqlite3
import json
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Enrich well contractors with pre-filtered EPA JSON data.")
    parser.add_argument("--db", type=str, required=True, help="Path to SQLite database.")
    parser.add_argument("--state", type=str, help="State abbreviation to filter by (e.g., GA)")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of records to process.")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"Database not found: {args.db}")
        return

    # Expected path for the pre-filtered JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "cache", "epa_sdwis", "epa_filtered_alerts.json")

    if not os.path.exists(json_path):
        print(f"\n[!] MISSING EPA PRE-FILTERED DATA [!]")
        print(f"Please run `python p3_prep_epa_data.py` first to generate the local repository.")
        return

    print("Loading lightweight EPA JSON repository...")
    with open(json_path, 'r', encoding='utf-8') as f:
        epa_lookup = json.load(f)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT id, state, county, served_counties FROM well_contractors WHERE local_epa_water_alerts IS NULL AND (county IS NOT NULL OR served_counties IS NOT NULL)"
    params = []
    
    if args.state:
        query += " AND state = ?"
        params.append(args.state.upper())
        
    query += " LIMIT ?"
    params.append(args.limit)

    c.execute(query, params)
    rows = c.fetchall()

    updates = []
    print(f"\nProcessing {len(rows)} records against local EPA data...")

    for row in rows:
        contractor_id = row["id"]
        state = row["state"]
        primary_county = row["county"]
        served_counties_str = row["served_counties"]

        counties_to_check = []
        if served_counties_str:
            counties_to_check = [cty.strip() for cty in served_counties_str.split(",") if cty.strip()]
        
        if not counties_to_check and primary_county:
            counties_to_check = [primary_county]

        if not state or not counties_to_check:
            continue

        all_alerts = {}
        for county in counties_to_check:
            clean_county = county.replace("County", "").replace("county", "").strip()
            state_prefix = f"{state}-".lower()
            if clean_county.lower().startswith(state_prefix):
                clean_county = clean_county[len(state_prefix):].strip()

            key = f"{state}_{clean_county}".lower()
            
            if key in epa_lookup and epa_lookup[key]:
                all_alerts[county] = {
                    "alerts": epa_lookup[key],
                    "disclaimer": "These EPA health violations occurred in public/municipal groundwater systems within this county in the last 5 years. Because private wells draw from the same regional aquifers, local well owners should consider having their water tested by a certified contractor for these contaminants."
                }

        alerts_json = json.dumps(all_alerts) if all_alerts else json.dumps({})
        updates.append((alerts_json, contractor_id))
        print(f"ID {contractor_id} - Found EPA alerts for {len(all_alerts)} counties.")

    if updates:
        c.executemany("UPDATE well_contractors SET local_epa_water_alerts = ? WHERE id = ?", updates)
        conn.commit()
        print(f"Successfully enriched {len(updates)} records.")
    
    conn.close()

if __name__ == "__main__":
    main()
