import csv
import sqlite3
import os

def main():
    csv_path = r"C:\Users\tamo4\Downloads\crSrch_export_1781739023621.csv"
    db_path = "02-workbench/03-wells-water-well-drillers/data/florida_wells.sqlite"
    
    if not os.path.exists(csv_path):
        print(f"[-] CSV file not found at: {csv_path}")
        return
        
    print(f"[*] Parsing well completion reports from {csv_path}...")
    
    # 1. Parse CSV and compute aggregated stats
    well_stats = {} # license -> {count, total_depth, valid_depth_count}
    
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        total_rows = 0
        for row in reader:
            total_rows += 1
            license_raw = row.get("License #")
            if not license_raw:
                continue
                
            lic_clean = license_raw.strip()
            if not lic_clean:
                continue
                
            depth_raw = row.get("Total Depth")
            depth_val = None
            if depth_raw:
                try:
                    depth_val = float(depth_raw.strip())
                    if depth_val <= 0:
                        depth_val = None
                except ValueError:
                    pass
                    
            if lic_clean not in well_stats:
                well_stats[lic_clean] = {"count": 0, "total_depth": 0.0, "valid_depth_count": 0}
                
            well_stats[lic_clean]["count"] += 1
            if depth_val is not None:
                well_stats[lic_clean]["total_depth"] += depth_val
                well_stats[lic_clean]["valid_depth_count"] += 1
                
    print(f"[+] Finished parsing {total_rows} rows from CSV.")
    print(f"[+] Aggregated stats for {len(well_stats)} unique licenses.")
    
    # 2. Connect to database and update records
    print(f"[*] Updating database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Reset existing values first to avoid stale data
    cursor.execute("UPDATE well_contractors SET wells_drilled_last_5_years = NULL, average_well_depth_ft = NULL")
    
    # Look up company mapping by license
    cursor.execute("SELECT license_number, company_id FROM technician_licenses")
    lic_to_company = {}
    for row in cursor.fetchall():
        lic_to_company[row[0].strip()] = row[1]
        
    updated_contractors = 0
    total_wells_updated = 0
    
    try:
        with conn:
            for lic, stats in well_stats.items():
                if lic in lic_to_company:
                    company_id = lic_to_company[lic]
                    count = stats["count"]
                    avg_depth = None
                    if stats["valid_depth_count"] > 0:
                        avg_depth = round(stats["total_depth"] / stats["valid_depth_count"])
                        
                    cursor.execute("""
                        UPDATE well_contractors
                        SET wells_drilled_last_5_years = ?, average_well_depth_ft = ?
                        WHERE id = ?
                    """, (count, avg_depth, company_id))
                    
                    updated_contractors += 1
                    total_wells_updated += count
                    
        print(f"[+] Successfully updated {updated_contractors} contractor listings.")
        print(f"[+] Total wells represented in database matches: {total_wells_updated}")
        
    except Exception as e:
        print(f"[-] Database update failed: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    main()
