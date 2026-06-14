from playwright.sync_api import sync_playwright
import json
import sqlite3
import os
import sys
import re

# Add general scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "general"))
from schema import initialize_database
from utils import get_db_path, slugify, clean_phone_number

def run_scraper():
    all_records = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_route(route):
            if "GetWaterwellDrillingCompaniesByName" in route.request.url and route.request.method == "POST":
                post_data = route.request.post_data
                if post_data:
                    # Modify pagination size to 1000
                    post_data = re.sub(r'"MaxRecords"\s*:\s*\d+', '"MaxRecords":1000', post_data)
                    post_data = re.sub(r'"MaxRecordsBusinessName"\s*:\s*\d+', '"MaxRecordsBusinessName":1000', post_data)
                    route.continue_(post_data=post_data)
                else:
                    route.continue_()
            else:
                route.continue_()
                
        def handle_response(response):
            if "screenservices" in response.url and "GetWaterwellDrillingCompaniesByName" in response.url and response.request.method == "POST":
                try:
                    data = response.json()
                    if 'data' in data and 'List' in data['data'] and 'List' in data['data']['List']:
                        records = data['data']['List']['List']
                        all_records.extend(records)
                        print(f"Captured {len(records)} records from API response.")
                except Exception as e:
                    print("Error parsing response:", e)

        page.route("**/*", handle_route)
        page.on("response", handle_response)
        
        print("Navigating to NY DEC Water Well Contractor Search...")
        page.goto("https://appfactory.dec.ny.gov/WaterWell/Contractor_Search", wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        print("Clicking Tab 2 (Search By Business Name)...")
        page.click("text=Search By Business Name")
        page.wait_for_timeout(1000)
        
        print("Searching for ' ' to get all records with modified pagination...")
        page.fill("#Input_BusinessName4", " ")
        page.wait_for_timeout(500)
        
        # Click search
        page.click("button:has-text('Search Contractors') >> nth=1")
        page.wait_for_timeout(5000) # Wait for response
        
        browser.close()
        
    return all_records

def process_and_save(records):
    db_path = get_db_path("new_york")
    initialize_database(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Let's clear the table first to avoid duplicates or incomplete previous runs
    c.execute("DELETE FROM installers_haulers")
    
    inserted = 0
    for rec in records:
        company = rec.get("DRILLING_COMPANY", {})
        
        name = company.get("NAME", "").strip()
        if not name:
            continue
            
        reg_num = company.get("REG_NUM", "").strip()
        slug = slugify(f"ny-{name}-{reg_num}")
        
        address = company.get("STREET", "").strip()
        city = company.get("CITY", "").strip()
        state = company.get("STATE", "NY").strip()
        zip_code = company.get("ZIP", "").strip()
        phone = clean_phone_number(company.get("PHONE", ""))
        
        try:
            c.execute("""
                INSERT INTO installers_haulers (
                    name, slug, address, city, state, zip_code, phone_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, slug, address, city, state, zip_code, phone))
            inserted += 1
        except sqlite3.IntegrityError:
            pass # Skip duplicates
            
    conn.commit()
    conn.close()
    
    print(f"Extraction complete. Inserted {inserted} records into {db_path}.")

if __name__ == "__main__":
    records = run_scraper()
    if records:
        # Deduplicate records by reg_num
        unique_records = {}
        for r in records:
            company = r.get("DRILLING_COMPANY", {})
            reg = company.get("REG_NUM")
            if reg:
                unique_records[reg] = r
                
        print(f"Total unique records found: {len(unique_records)}")
        process_and_save(list(unique_records.values()))
    else:
        print("No records were found.")
