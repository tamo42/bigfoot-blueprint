import subprocess
import time
import sqlite3
import os
import sys

WORKSPACE = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint"
DB_PATH = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-closing-attorneys\data\directory.sqlite"
CACHE_DIR = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-closing-attorneys\cache\crawled_text\georgia-closing-attorneys"

def get_pending_count():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(id) FROM attorneys WHERE faq_enriched IS NULL AND website_url IS NOT NULL AND website_url != 'NOT_FOUND'")
        total = c.fetchone()[0]
        conn.close()
        return total
    except Exception as e:
        print(f"DB Error: {e}")
        return 99999

def mark_failed_records():
    """
    Error Correction:
    The crawler creates a .failed file when a website cannot be reached.
    If we leave them, they stay faq_enriched=NULL forever, stalling the loop.
    This function updates their status to 'FAILED' so the loop can finish cleanly.
    """
    try:
        if not os.path.exists(CACHE_DIR):
            return
            
        failed_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.failed')]
        if not failed_files:
            return
            
        failed_ids = [f.split('.')[0] for f in failed_files]
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        updated = 0
        chunk_size = 900
        for i in range(0, len(failed_ids), chunk_size):
            chunk = failed_ids[i:i+chunk_size]
            placeholders = ",".join("?" for _ in chunk)
            c.execute(f"UPDATE attorneys SET faq_enriched = 'FAILED' WHERE id IN ({placeholders}) AND faq_enriched IS NULL", chunk)
            updated += c.rowcount
            
        conn.commit()
        conn.close()
        
        if updated > 0:
            print(f"[!] Error Correction: Marked {updated} unreachable websites as FAILED in DB.")
            
    except Exception as e:
        print(f"[-] Error marking failed records: {e}")

def run_loop():
    last_count = -1
    stagnant_loops = 0
    batch = 0
    batch_size = 100

    print("==================================================")
    print("Starting Continuous Background Batch Loop")
    print("==================================================")

    while True:
        batch += 1
        mark_failed_records() # Clean up failed records before counting
        
        remaining = get_pending_count()
        print(f"\n======================================")
        print(f"[*] Batch {batch} | Remaining pending records: {remaining}")
        print(f"======================================")
        
        if remaining <= 0:
            print("[+] All valid records have been enriched! Stopping the background loop.")
            break
            
        if remaining == last_count:
            stagnant_loops += 1
            if stagnant_loops >= 3:
                print("[-] Remaining count hasn't changed for 3 cycles. Breaking to prevent infinite loop.")
                break
        else:
            stagnant_loops = 0
            
        last_count = remaining
        
        scripts_dir = r"02-workbench\georgia-closing-attorneys\scripts"
        
        try:
            # 1. Crawl
            print("\n[1/4] Crawling next 100 sites...")
            subprocess.run([
                sys.executable, 
                r"scripts\p3_crawl_websites.py", 
                "--db", DB_PATH,
                "--table", "attorneys",
                "--id-column", "id",
                "--cache-dir", CACHE_DIR,
                "--keywords", "service,about,practice,real,estate,closing,contact,attorney,law",
                "--limit", str(batch_size)
            ], cwd=WORKSPACE, check=False)
            
            # 2. Extract Specialties offline
            print("\n[2/4] Resetting and extracting offline specialties...")
            subprocess.run([sys.executable, f"{scripts_dir}\\reset_specialties.py"], cwd=WORKSPACE, check=False)
            subprocess.run([sys.executable, f"{scripts_dir}\\p3_enrich_specialties.py", "--limit", str(batch_size)], cwd=WORKSPACE, check=False)
            
            # 3. AI Enrichment
            print("\n[3/4] Running Gemini LLM Enrichment Engine...")
            subprocess.run([sys.executable, f"{scripts_dir}\\p3_enrich_listings.py", "--limit", str(batch_size)], cwd=WORKSPACE, check=False)
            
            # 4. Validation Gate
            print("\n[4/4] Validating records through the Anti-Thin-Content Gate...")
            subprocess.run([sys.executable, f"{scripts_dir}\\p3_validate_database.py"], cwd=WORKSPACE, check=False)
            
            # Git Push
            print("\n[*] Saving progress to Git...")
            subprocess.run(["git", "add", r"02-workbench\georgia-closing-attorneys\data\directory.sqlite"], cwd=WORKSPACE, check=False)
            subprocess.run(["git", "commit", "-m", f"Auto-commit: GA Closing Attorneys enriched data (batch {batch})"], cwd=WORKSPACE, check=False)
            subprocess.run(["git", "push"], cwd=WORKSPACE, check=False)
            
        except Exception as e:
            print(f"[-] Error during batch {batch} execution: {e}")
        
        print(f"\n[+] Batch {batch} complete. Cooling down for 5 seconds before next cycle...")
        time.sleep(5)

if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    run_loop()
