import subprocess
import time
import sqlite3
import os
import sys

WORKSPACE = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint"
DB_PATH = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\water-well-drillers\data\water_well_directory.sqlite"

def get_remaining():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM well_contractors WHERE data_freshness IS NULL OR data_freshness != 'enriched'")
        total = c.fetchone()[0]
        conn.close()
        return total
    except Exception as e:
        print(f"DB Error: {e}")
        return 99999

def run_loop():
    last_count = -1
    stagnant_loops = 0
    batch = 0

    while True:
        batch += 1
        remaining = get_remaining()
        print(f"\n======================================")
        print(f"[*] Batch {batch} | Remaining unenriched records: {remaining}")
        print(f"======================================")
        
        if remaining <= 0:
            print("[+] All records are enriched! Stopping the background loop.")
            break
            
        if remaining == last_count:
            stagnant_loops += 1
            if stagnant_loops >= 3:
                print("[-] Remaining count hasn't changed for 3 cycles. Possible un-enrichable records. Exiting.")
                break
        else:
            stagnant_loops = 0
            
        last_count = remaining
        
        # 1. Apify
        print("\n[*] 1/3: Running Apify enrichment...")
        subprocess.run([
            sys.executable, 
            r"scripts\p3_enrich_places_apify.py", 
            "--state", "all", 
            "--limit", "100",
            "--db", DB_PATH
        ], cwd=WORKSPACE)
        
        # 2. Crawl
        print("\n[*] 2/3: Running Website Crawler...")
        subprocess.run([
            sys.executable, 
            r"scripts\p3_crawl_websites.py", 
            "--db", DB_PATH,
            "--table", "well_contractors",
            "--id-column", "slug",
            "--cache-dir", r"C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\water-well-drillers\cache\crawled_text\general",
            "--keywords", "service,about,capability,drilling,pump,contact,water,filter,inspect",
            "--limit", "100",
            "--workers", "5",
            "--where", "data_freshness IS NULL OR data_freshness != 'enriched'"
        ], cwd=WORKSPACE)
        
        # 3. Gemini
        print("\n[*] 3/3: Running Gemini enrichment...")
        subprocess.run(["python", "02-workbench/water-well-drillers/scripts/general/p3_enrich_listings.py", "--mode", "full", "--state", "all"], cwd=WORKSPACE)
        
        # Git Push
        print("\n[*] Saving progress to Git...")
        subprocess.run(["git", "add", "."], cwd=WORKSPACE)
        subprocess.run(["git", "commit", "-m", f"feat(enrichment): background batch {batch} of 100 complete"], cwd=WORKSPACE)
        subprocess.run(["git", "push"], cwd=WORKSPACE)
        
        print(f"\n[+] Batch {batch} complete. Waiting 5 seconds before next cycle...")
        time.sleep(5)

if __name__ == "__main__":
    # Ensure stdout is unbuffered so logs stream in real-time
    sys.stdout.reconfigure(line_buffering=True)
    run_loop()
