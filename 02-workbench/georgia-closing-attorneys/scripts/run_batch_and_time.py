import time
import subprocess
import os
import sys

def main():
    print("==================================================")
    print("Timing next batch of 100 records...")
    print("==================================================")
    
    start_time = time.time()
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Crawl
    print("[1/4] Running p3_crawl_websites.py --limit 100")
    t0 = time.time()
    subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_crawl_websites.py"), "--limit", "100"], check=False)
    print(f"      => Crawl took {time.time() - t0:.1f}s")
    
    # 2. Extract Specialties offline
    print("\n[2/4] Running reset_specialties.py then p3_enrich_specialties.py --limit 100")
    t0 = time.time()
    subprocess.run([sys.executable, os.path.join(scripts_dir, "reset_specialties.py")], check=False)
    subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_enrich_specialties.py"), "--limit", "100"], check=False)
    print(f"      => Specialties offline extraction took {time.time() - t0:.1f}s")
    
    # 3. AI Enrichment
    print("\n[3/4] Running p3_enrich_listings.py --limit 100")
    t0 = time.time()
    subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_enrich_listings.py"), "--limit", "100"], check=False)
    print(f"      => AI Enrichment took {time.time() - t0:.1f}s")
    
    # 4. Validation Gate
    print("\n[4/4] Running p3_validate_database.py")
    t0 = time.time()
    subprocess.run([sys.executable, os.path.join(scripts_dir, "p3_validate_database.py")], check=False)
    print(f"      => Validation Gate took {time.time() - t0:.1f}s")
    
    total_time = time.time() - start_time
    print("==================================================")
    print(f"TOTAL TIME FOR 100 RECORDS: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    
    remaining = 2700
    estimated_seconds = (total_time / 100) * remaining
    print(f"ESTIMATED TIME FOR {remaining} RECORDS: {estimated_seconds/3600:.1f} hours")
    print("==================================================")

if __name__ == "__main__":
    main()
