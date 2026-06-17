import os
import json
import sqlite3
import argparse
from p3_utils import get_unified_db_path
from p3_schema import initialize_database

def enrich_well_logs(db_path, limit=None, target_state=None):
    """
    Reads the pre-processed county groundwater stats JSON and enriches the well_contractors
    table with hyper-local average well depth and yield based on their service area.
    """
    STATE_MAP = {
        'AL': 'ALABAMA', 'AK': 'ALASKA', 'AZ': 'ARIZONA', 'AR': 'ARKANSAS', 'CA': 'CALIFORNIA',
        'CO': 'COLORADO', 'CT': 'CONNECTICUT', 'DE': 'DELAWARE', 'FL': 'FLORIDA', 'GA': 'GEORGIA',
        'HI': 'HAWAII', 'ID': 'IDAHO', 'IL': 'ILLINOIS', 'IN': 'INDIANA', 'IA': 'IOWA',
        'KS': 'KANSAS', 'KY': 'KENTUCKY', 'LA': 'LOUISIANA', 'ME': 'MAINE', 'MD': 'MARYLAND',
        'MA': 'MASSACHUSETTS', 'MI': 'MICHIGAN', 'MN': 'MINNESOTA', 'MS': 'MISSISSIPPI',
        'MO': 'MISSOURI', 'MT': 'MONTANA', 'NE': 'NEBRASKA', 'NV': 'NEVADA', 'NH': 'NEW HAMPSHIRE',
        'NJ': 'NEW JERSEY', 'NM': 'NEW MEXICO', 'NY': 'NEW YORK', 'NC': 'NORTH CAROLINA',
        'ND': 'NORTH DAKOTA', 'OH': 'OHIO', 'OK': 'OKLAHOMA', 'OR': 'OREGON', 'PA': 'PENNSYLVANIA',
        'RI': 'RHODE ISLAND', 'SC': 'SOUTH CAROLINA', 'SD': 'SOUTH DAKOTA', 'TN': 'TENNESSEE',
        'TX': 'TEXAS', 'UT': 'UTAH', 'VT': 'VERMONT', 'VA': 'VIRGINIA', 'WA': 'WASHINGTON',
        'WV': 'WEST VIRGINIA', 'WI': 'WISCONSIN', 'WY': 'WYOMING'
    }

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cache_file = os.path.join(base_dir, "cache", "well_logs", "county_groundwater_stats.json")

    if not os.path.exists(cache_file):
        print(f"[-] Error: Cache file not found at {cache_file}. Run p3_prep_well_logs.py first.")
        return

    print("[+] Loading pre-processed USGWD county stats...")
    with open(cache_file, 'r', encoding='utf-8') as f:
        stats_cache = json.load(f)

    print(f"[+] Connecting to database: {db_path}")
    initialize_database(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT id, name, state, county, served_counties FROM well_contractors WHERE local_groundwater_conditions IS NULL"
    params = []
    
    if target_state:
        query += " AND state = ?"
        params.append(target_state)
        
    if limit:
        query += f" LIMIT {limit}"

    c.execute(query, params)
    rows = c.fetchall()
    
    if not rows:
        print("[+] No un-enriched records found.")
        conn.close()
        return

    print(f"[+] Found {len(rows)} records to enrich with local groundwater conditions.")

    updates = []
    enrichment_count = 0

    for row in rows:
        contractor_id = row['id']
        c_state = row['state']
        c_county = row['county']
        served_counties_str = row['served_counties']

        if not c_state:
            continue

        c_state_full = STATE_MAP.get(c_state.upper(), c_state.upper())
        target_counties = []

        # Determine which counties to check
        if served_counties_str:
            try:
                parsed_counties = json.loads(served_counties_str)
                if isinstance(parsed_counties, list):
                    for x in parsed_counties:
                        clean_county = str(x).upper().replace(" COUNTY", "").strip()
                        if "-" in clean_county:
                            clean_county = clean_county.split("-")[-1].strip()
                        target_counties.append(clean_county)
            except json.JSONDecodeError:
                pass

        # Fallback to primary county if no served counties parsed
        if not target_counties and c_county:
             clean_county = c_county.upper().replace(" COUNTY", "").strip()
             if "-" in clean_county:
                 clean_county = clean_county.split("-")[-1].strip()
             target_counties = [clean_county]

        if not target_counties:
            continue

        # Look up stats
        contractor_stats = {}
        for county in target_counties:
            # Check state exists in cache
            if c_state_full in stats_cache:
                # Direct match
                if county in stats_cache[c_state_full]:
                    contractor_stats[f"{c_state}-{county}"] = stats_cache[c_state_full][county]
                else:
                    # Try fuzzy matching without suffixes if direct match fails
                    for cache_county, data in stats_cache[c_state_full].items():
                        if cache_county in county or county in cache_county:
                            contractor_stats[f"{c_state}-{cache_county}"] = data
                            break

        if contractor_stats:
            # Add disclaimer for the UI
            contractor_stats["disclaimer"] = "These groundwater conditions represent the average depth and yield of wells constructed in the last 10 years within the specified county, based on the United States Groundwater Well Database (USGWD)."
            
            updates.append((json.dumps(contractor_stats), contractor_id))
            enrichment_count += 1
        else:
            updates.append((json.dumps({}), contractor_id))

    # Apply batch update
    if updates:
        print(f"\n[+] Applying {len(updates)} database updates...")
        c.executemany("UPDATE well_contractors SET local_groundwater_conditions = ? WHERE id = ?", updates)
        conn.commit()
    
    print(f"[+] Successfully enriched {enrichment_count} contractor listings with local groundwater conditions.")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich contractor listings with local groundwater stats")
    parser.add_argument("--db", default=None, help="Path to SQLite database")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to process")
    parser.add_argument("--state", default=None, help="Filter by specific state (e.g., GA)")
    
    args = parser.parse_args()
    
    db_path = args.db if args.db else get_unified_db_path()
    enrich_well_logs(db_path, args.limit, args.state)
