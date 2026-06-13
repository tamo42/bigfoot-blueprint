import sqlite3
import random
import time
import json
import os
import re
from playwright.sync_api import sync_playwright

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/directory.sqlite')
LIMIT = 50 # Iteration 3: Batch of 50

def human_delay(min_sec=3.0, max_sec=8.5):
    """Introduces a randomized delay 'jiggle' to mimic human interaction."""
    delay = random.uniform(min_sec, max_sec)
    print(f"[*] Human-mimicking delay: sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

def scrape_website_for_underwriters(page, url):
    """
    Visits the firm's website and searches the homepage text for mentions of the Big Four underwriters.
    """
    appointments = []
    if not url or url == 'NOT_FOUND':
        print("      [-] No valid website URL provided.")
        return appointments
        
    if not url.startswith('http'):
        url = 'https://' + url
        
    print(f"  [*] Scraping firm website: {url}...")
    try:
        # 15 second timeout to avoid hanging on dead sites
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        human_delay(2.0, 4.0)
        
        # Grab text of the whole page
        body_text = page.locator('body').inner_text().lower()
        
        # Check for underwriter mentions
        if "first american" in body_text:
            appointments.append("First American Title")
            print("      [+] Found mention of First American!")
        if "fidelity national" in body_text or "chicago title" in body_text or "commonwealth land" in body_text:
            appointments.append("Fidelity National Title")
            print("      [+] Found mention of Fidelity/Chicago Title!")
        if "stewart title" in body_text:
            appointments.append("Stewart Title")
            print("      [+] Found mention of Stewart Title!")
        if "old republic" in body_text:
            appointments.append("Old Republic Title")
            print("      [+] Found mention of Old Republic!")
            
        if not appointments:
            print("      [-] No underwriter mentions found on homepage.")
            
    except Exception as e:
        print(f"      [!] Website scrape error: {e}")
        
    return list(set(appointments))

def run_enrichment():
    print(f"=========================================================")
    print(f"Underwriters Locator Enrichment Iteration 3 (LIMIT: {LIMIT})")
    print(f"=========================================================")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Fetch 50 records that previously yielded no results ('[]') AND have a website
    c.execute('''
        SELECT id, first_name, last_name, firm_name, city, website_url 
        FROM attorneys 
        WHERE appointments = '[]' AND website_url IS NOT NULL AND website_url != 'NOT_FOUND'
        LIMIT ?
    ''', (LIMIT,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending records with websites found for Iteration 3.")
        return
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for row in records:
            attorney_id = row['id']
            first_name = row['first_name']
            last_name = row['last_name']
            firm_name = row['firm_name'] or ""
            city = row['city']
            website_url = row['website_url']
            
            display_name = firm_name if firm_name else f"{first_name} {last_name}"
            print(f"\nProcessing ID {attorney_id}: {display_name} ({city})")
            
            appointments = scrape_website_for_underwriters(page, website_url)
            
            # Since this is a retry phase, we only update if we actually found something
            if appointments:
                appointments_json = json.dumps(appointments)
                print(f"  [+] Discovered appointments: {appointments_json}")
                
                c.execute('''
                    UPDATE attorneys
                    SET appointments = ?
                    WHERE id = ?
                ''', (appointments_json, attorney_id))
                
                conn.commit()
                print(f"  [+] Updated ID {attorney_id} in database.")
            
            print("  [*] Applying inter-record jitter delay to avoid IP blocks...")
            human_delay(3.0, 7.5)
            
        browser.close()
        
    conn.close()
    print("\n=========================================================")
    print("Iteration 3 Batch Complete")
    print("=========================================================")

if __name__ == "__main__":
    run_enrichment()


