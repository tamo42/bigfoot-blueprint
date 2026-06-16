import subprocess
import sys
import os

WORKSPACE = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint"
DB_PATH = r"C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\data\water_well_directory.sqlite"

def main():
    print("\n[*] 1/3: Running Apify enrichment...")
    subprocess.run([sys.executable, "02-workbench/03-wells-water-well-drillers/scripts/general/p3_enrich_places_apify.py", "--state", "all", "--limit", "100"], cwd=WORKSPACE)
    
    print("\n[*] 2/3: Running Website Crawler...")
    subprocess.run([
        sys.executable, 
        r"scripts\p3_crawl_websites.py", 
        "--db", DB_PATH,
        "--table", "well_contractors",
        "--id-column", "slug",
        "--cache-dir", r"C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\cache\crawled_text\general",
        "--keywords", "service,about,capability,drilling,pump,contact,water,filter,inspect",
        "--limit", "100",
        "--workers", "5"
    ], cwd=WORKSPACE)
    
    print("\n[*] 3/3: Running Gemini enrichment...")
    subprocess.run([sys.executable, "02-workbench/03-wells-water-well-drillers/scripts/general/p3_enrich_listings.py", "--mode", "full", "--state", "all", "--limit", "100"], cwd=WORKSPACE)
    
    print("\n[*] Saving progress to Git...")
    subprocess.run(["git", "add", "."], cwd=WORKSPACE)
    subprocess.run(["git", "commit", "-m", "feat(enrichment): test batch of 100 complete"], cwd=WORKSPACE)
    subprocess.run(["git", "push"], cwd=WORKSPACE)
    
    print("\n[+] Test batch complete!")

if __name__ == "__main__":
    # Ensure stdout is unbuffered so logs stream in real-time
    sys.stdout.reconfigure(line_buffering=True)
    main()
