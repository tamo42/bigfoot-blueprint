import time
import subprocess
import os
import sys
import sqlite3

def get_pending_count(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM attorneys WHERE faq_enriched IS NULL AND website_url IS NOT NULL AND website_url != 'NOT_FOUND'")
    count = c.fetchone()[0]
    conn.close()
    return count

def main():
    print("==================================================")
    print("Starting Continuous Background Batch Loop")
    print("==================================================")
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(scripts_dir, "..", "data", "directory.sqlite"))
    
    batch_size = 100
    batch_num = 1
    
    while True:
        pending = get_pending_count(db_path)
        if pending == 0:
            print("\n[+] All valid records have been enriched. Background loop complete!")
            break
            
        print(f"\n--- Starting Batch {batch_num} ---")
        print(f"Remaining pending records: {pending}")
        
        start_time = time.time()
        
        print(f"[1/4] Crawling next {batch_size} sites...")
        subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_crawl_websites.py"), "--limit", str(batch_size)], check=False)
        
        print("[2/4] Resetting and extracting offline specialties...")
        subprocess.run([sys.executable, os.path.join(scripts_dir, "reset_specialties.py")], check=False)
        subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_enrich_specialties.py"), "--limit", str(batch_size)], check=False)
        
        print("[3/4] Running Gemini LLM Enrichment Engine...")
        subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_enrich_listings.py"), "--limit", str(batch_size)], check=False)
        
        print("[4/4] Validating records through the Anti-Thin-Content Gate...")
        subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_validate_database.py")], check=False)
        
        elapsed = time.time() - start_time
        print(f"--- Batch {batch_num} complete in {elapsed/60:.1f} minutes ---")
        
        batch_num += 1
        
        print("Cooling down for 5 seconds before next batch...")
        time.sleep(5)

if __name__ == "__main__":
    main()
