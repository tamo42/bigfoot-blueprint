import sqlite3
import os
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

def get_search_queries(name):
    queries = []
    
    # 1. Cleaned full name
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
    cleaned = ' '.join(cleaned.split())
    if cleaned:
        queries.append(cleaned)
        
    # 2. Remove common business suffixes and industry terms
    no_suffix = re.sub(r'\b(dba|llc|inc|corp|co|ltd|corporation|incorporated|company|limited|liability|plumbing|septic|services|environmental|construction|sanitary|and|&)\b', '', cleaned, flags=re.IGNORECASE)
    no_suffix = ' '.join(no_suffix.split())
    if no_suffix and no_suffix not in queries:
        queries.append(no_suffix)
        
    # 3. First two words fallback
    words = cleaned.split()
    if len(words) > 2:
        two_words = ' '.join(words[:2])
        if two_words not in queries:
            queries.append(two_words)
            
    return queries

import re

def search_company(page, query_name):
    try:
        # Navigate to search portal
        page.goto("https://ecorp.sos.ga.gov/BusinessSearch")
        time.sleep(random.uniform(2.0, 3.5))
        
        # Fill search input
        page.fill("#txtBusinessName", query_name)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Click search
        page.click("#btnSearch")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Check if results exist
        if "No records found" in page.content():
            return None
            
        rows = page.query_selector_all("table tr")
        best_status = None
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) == 6:
                row_data = [c.inner_text().strip() for c in cells]
                # Columns: Business Name, Control Number, Business Type, Principal Office Address, Registered Agent, Status
                status = row_data[5]
                # Prioritize any Active status if multiple rows match the search query
                if "Active" in status:
                    return status
                best_status = status
        return best_status
    except Exception as e:
        print(f"Error searching {query_name}: {e}")
    return None

def main():
    db_path = r"C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query only haulers that haven't been verified yet (incremental resume support)
    cursor.execute("SELECT id, name FROM installers_haulers WHERE post_status = 'publish' AND sos_status IS NULL")
    rows = cursor.fetchall()
    
    print(f"Loaded {len(rows)} unverified haulers for eCorp verification.")
    
    if not rows:
        print("All haulers have already been processed.")
        conn.close()
        return
        
    with sync_playwright() as p:
        # Launch using Chrome channel and disable automation-controlled flag
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        # Evade webdriver detection
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        for row in rows:
            hauler_id, name = row
            print(f"\n--- Verifying: {name} ---")
            
            queries = get_search_queries(name)
            status = None
            
            for query in queries:
                print(f"Trying search query: '{query}'")
                status = search_company(page, query)
                if status:
                    break
                # Small wait between query retries
                time.sleep(random.uniform(1.0, 2.0))
            
            if status:
                current_date = datetime.now().strftime("%Y-%m-%d")
                print(f"Match found! Status: {status} (Verified: {current_date})")
                cursor.execute("""
                    UPDATE installers_haulers
                    SET sos_status = ?,
                        sos_last_checked = ?
                    WHERE id = ?
                """, (status, current_date, hauler_id))
            else:
                # If no match is found, store 'Unverified' so we don't query it again in future runs
                current_date = datetime.now().strftime("%Y-%m-%d")
                print(f"No match found on Georgia eCorp for '{name}' after checking all candidates. Setting status as Unverified.")
                cursor.execute("""
                    UPDATE installers_haulers
                    SET sos_status = 'Unverified',
                        sos_last_checked = ?
                    WHERE id = ?
                """, (current_date, hauler_id))
                
            # Commit after each entry so progress is saved incrementally
            conn.commit()
            
            # Random delay before next company search to look human
            time.sleep(random.uniform(4.0, 8.0))
            
        browser.close()
        
    conn.close()
    print("\neCorp verification complete.")

if __name__ == "__main__":
    main()
