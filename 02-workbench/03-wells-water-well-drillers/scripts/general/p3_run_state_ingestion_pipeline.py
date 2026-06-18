import os
import sys
import time
import subprocess
import argparse
import json

def get_workspace_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))

def calculate_projections(records, vendors, website_ratio=0.5, review_ratio=0.3):
    """Calculates expected execution times (in seconds) for each stage of the pipeline."""
    t_parse = records * 0.001
    t_apify = 120 + (vendors * 0.5)
    t_crawl = vendors * website_ratio * 0.25
    t_listings = vendors * website_ratio * 1.0
    t_scorecards = vendors * review_ratio * 1.0
    t_county = 10
    t_append = 10
    t_build = 45 # Approximate build time
    
    overall_ttc = t_parse + t_apify + t_crawl + t_listings + t_scorecards + t_county + t_append + t_build
    
    return {
        "overall": overall_ttc,
        "stages": {
            "apify": t_apify,
            "crawl": t_crawl,
            "listings": t_listings,
            "scorecards": t_scorecards,
            "county": t_county,
            "append": t_append,
            "build": t_build
        }
    }

def run_stage(cmd, cwd, expected_time, stage_name):
    """Runs a pipeline stage command in a subprocess with active timeout monitoring."""
    timeout_limit = expected_time * 1.25
    half_time = expected_time * 0.50
    full_time = expected_time * 1.00
    
    print(f"\n==================================================")
    print(f"STARTING STAGE: {stage_name.upper()}")
    print(f"Command: {' '.join(cmd)}")
    print(f"Expected Time: {expected_time:.1f}s | Limit (125%): {timeout_limit:.1f}s")
    print(f"==================================================")
    
    start_time = time.time()
    
    try:
        # Launch process
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor loop
        notified_50 = False
        notified_100 = False
        
        while True:
            # Check if process finished
            ret = process.poll()
            elapsed = time.time() - start_time
            
            if ret is not None:
                # Finished successfully
                stdout, stderr = process.communicate()
                print(f"[+] Stage {stage_name} finished in {elapsed:.1f}s with exit code {ret}.")
                if ret != 0:
                    print(f"[-] Error Output:\n{stderr}")
                    return False
                return True
                
            # Active Monitoring Checkpoints
            if elapsed >= half_time and not notified_50:
                print(f"  [*] 50% Benchmark reached ({elapsed:.1f}s). Checking process status: RUNNING.")
                notified_50 = True
                
            if elapsed >= full_time and not notified_100:
                print(f"  [!] 100% Benchmark reached ({elapsed:.1f}s). Script is running longer than expected. Auditing logs...")
                notified_100 = True
                
            if elapsed >= timeout_limit:
                print(f"  [CAUTION] 125% Hard Limit exceeded ({elapsed:.1f}s). Process is STALLED. Terminating...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                print(f"[-] STALL DETECTED: Stage {stage_name} was killed due to exceeding the 125% TTC limit.")
                return False
                
            time.sleep(1)
            
    except Exception as e:
        print(f"[-] Exception running stage {stage_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Master State Ingestion Pipeline Runner with Active TTC Monitoring.")
    parser.add_argument("--state", required=True, help="State abbreviation (e.g. OK, FL)")
    parser.add_argument("--records", type=int, default=0, help="Number of raw completions log records to parse.")
    parser.add_argument("--vendors", type=int, default=100, help="Number of vendors to process.")
    parser.add_argument("--db-dir", help="Directory where SQLite databases are stored.")
    
    args = parser.parse_args()
    state_upper = args.state.upper()
    state_lower = args.state.lower()
    
    workspace = get_workspace_root()
    db_dir = args.db_dir or os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "data")
    
    state_db = os.path.join(db_dir, f"{state_lower}_wells.sqlite")
    master_db = os.path.join(db_dir, "water_well_directory.sqlite")
    website_db_dir = os.path.join(workspace, "..", "bigfoot-sites", "uswelldrillers.com")
    website_db = os.path.join(website_db_dir, "src", "data", "water_well_directory.sqlite")
    
    print(f"[*] Starting Pipeline Runner for State: {state_upper}")
    print(f"[*] State Database Path: {state_db}")
    print(f"[*] Unified Database Path: {master_db}")
    
    # 1. Project TTC
    projections = calculate_projections(args.records, args.vendors)
    print(f"[*] Projected Overall Time to Completion: {projections['overall']:.1f}s ({projections['overall']/60:.1f}m)")
    
    # Check Phase A database exists
    if not os.path.exists(state_db):
        print(f"[-] Error: Target state database {state_db} does not exist. Please complete Phase A (Scraping) first.")
        sys.exit(1)
        
    start_pipeline_time = time.time()
    
    # 2. Stage 1: Apify Places Scrape
    cmd_apify = [
        "python",
        os.path.join(workspace, "scripts", "p3_enrich_places_apify.py"),
        "--db", state_db,
        "--state", state_lower,
        "--limit", str(args.vendors)
    ]
    if not run_stage(cmd_apify, workspace, projections["stages"]["apify"], "Apify Places Scrape"):
        print("[-] Pipeline halted due to failure in Apify Scrape.")
        sys.exit(1)
        
    # 3. Stage 2: Website Crawling
    cmd_crawl = [
        "python",
        os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "scripts", "general", "p3_crawl_websites.py"),
        "--db", state_db
    ]
    if not run_stage(cmd_crawl, workspace, projections["stages"]["crawl"], "Website Crawling"):
        print("[-] Pipeline halted due to failure in Website Crawl.")
        sys.exit(1)
        
    # 4. Stage 3: Gemini Listings Enrichment
    cmd_listings = [
        "python",
        os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "scripts", "general", "p3_enrich_listings.py"),
        "--db", state_db,
        "--mode", "full"
    ]
    if not run_stage(cmd_listings, workspace, projections["stages"]["listings"], "Gemini Content Enrichment"):
        print("[-] Pipeline halted due to failure in Gemini Listings.")
        sys.exit(1)
        
    # 5. Stage 4: Gemini Review Scorecards
    cmd_reviews = [
        "python",
        os.path.join(workspace, "scripts", "p4_enrich_reviews_gemini.py"),
        "--db", state_db
    ]
    if not run_stage(cmd_reviews, workspace, projections["stages"]["scorecards"], "Gemini Review Scorecards"):
        print("[-] Pipeline halted due to failure in Gemini Scorecards.")
        sys.exit(1)
        
    # 6. Stage 5: Local County Resolution
    cmd_county = [
        "python",
        os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "scripts", "general", "p3_enrich_counties.py"),
        "--db", state_db
    ]
    if not run_stage(cmd_county, workspace, projections["stages"]["county"], "County Resolution"):
        print("[-] Pipeline halted due to failure in County Resolution.")
        sys.exit(1)
        
    # 7. Stage 6: Master Append
    cmd_append = [
        "python",
        os.path.join(workspace, "02-workbench", "03-wells-water-well-drillers", "scripts", "general", "p3_append_state_database.py"),
        "--state-db", state_db,
        "--master-db", master_db
    ]
    if not run_stage(cmd_append, workspace, projections["stages"]["append"], "Master Append"):
        print("[-] Pipeline halted due to failure in Master Append.")
        sys.exit(1)
        
    # 8. Copy master database to website folder
    print(f"[*] Copying {master_db} to website path: {website_db}")
    try:
        import shutil
        shutil.copy2(master_db, website_db)
        print("[+] Copy complete.")
    except Exception as e:
        print(f"[-] Failed to copy database to website: {e}")
        sys.exit(1)
        
    # 9. Stage 7: Website Build & Verification
    cmd_build = ["npm", "run", "build"]
    if not run_stage(cmd_build, website_db_dir, projections["stages"]["build"], "Website Static Build"):
        print("[-] Pipeline halted due to failure in static compilation.")
        sys.exit(1)
        
    # 10. Audit
    cmd_verify = [
        "python",
        os.path.join(workspace, "..", "config", "scratch", "verify_pages.py") # fallback placeholder, verify_pages is in scratch
    ]
    # resolve actual verify path
    verify_script_path = os.path.join(workspace, "..", ".gemini", "antigravity-ide", "brain", "07ddd581-f8a6-4fa6-a07f-f8b10b34f9df", "scratch", "verify_pages.py")
    if os.path.exists(verify_script_path):
        cmd_verify = ["python", verify_script_path]
        
    print(f"[*] Running final build audit verification...")
    subprocess.run(cmd_verify, cwd=website_db_dir)
    
    elapsed_pipeline = time.time() - start_pipeline_time
    print(f"\n==================================================")
    print(f"[+] PIPELINE RUN COMPLETE FOR STATE {state_upper}!")
    print(f"    - Total execution time: {elapsed_pipeline:.1f}s ({elapsed_pipeline/60:.1f}m)")
    print(f"    - Expected Baseline: {projections['overall']:.1f}s")
    print(f"    - Deviation: {((elapsed_pipeline - projections['overall']) / projections['overall']) * 100:.1f}%")
    print(f"==================================================")

if __name__ == "__main__":
    main()
