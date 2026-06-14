import os
import sys
import asyncio
import sqlite3
import re
from playwright.async_api import async_playwright

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

db_path = utils.get_db_path("michigan")

async def scrape_powerbi_grid():
    records_set = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("[*] Navigating to Michigan EGLE PowerBI page...")
        await page.goto('https://app.powerbigov.us/view?r=eyJrIjoiM2E0Y2ExMDctMzhmNC00MzY2LThjNmUtMjQ4Yzg2OTM4MjQ2IiwidCI6ImQ1ZmI3MDg3LTM3NzctNDJhZC05NjZhLTg5MmVmNDcyMjVkMSJ9', wait_until='networkidle')
        
        print("[*] Waiting for dashboard to load...")
        await page.wait_for_timeout(10000) 
        
        previous_len = 0
        scroll_attempts = 0
        
        while scroll_attempts < 20: 
            rows = await page.query_selector_all('div[role="row"]')
            if not rows:
                break
                
            for r in rows:
                text = await r.inner_text()
                if text.strip() and "Registration" not in text:
                    records_set.add(text.strip())
            
            if len(records_set) > previous_len:
                print(f"[+] Found {len(records_set)} records so far...")
                previous_len = len(records_set)
                scroll_attempts = 0
            else:
                scroll_attempts += 1
                
            # Scroll the last row into view
            try:
                await rows[-1].scroll_into_view_if_needed()
                await page.mouse.wheel(0, 500)
            except:
                pass
                
            await page.wait_for_timeout(1000)
            
        await browser.close()
        
    return list(records_set)

def parse_and_save(raw_records):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    unique_companies = {}
    
    for raw in raw_records:
        lines = [line.strip() for line in raw.split('\n') if line.strip()]
        
        # Expected format:
        # 0: Select Row (ignore if present)
        if lines and lines[0] == "Select Row":
            lines = lines[1:]
            
        # 0: County
        # 1: Contractor Name
        # 2: Business Name
        # 3: Address, City, MI ZIP
        # 4: Phone
        # 5: Contractor Type
        # 6: License Number
        
        if len(lines) < 7:
            continue
            
        county = lines[0]
        contractor_name = lines[1]
        business_name = lines[2]
        address_full = lines[3]
        phone = lines[4]
        contractor_type = lines[5]
        license_num = lines[6]
        
        # Parse Address
        # "2540 Hasler Road, Lapeer, MI 48446"
        addr_parts = [p.strip() for p in address_full.split(',')]
        if len(addr_parts) >= 3:
            city = addr_parts[-2]
            state_zip = addr_parts[-1].split(' ')
            state = state_zip[0]
            zip_code = state_zip[1] if len(state_zip) > 1 else ""
            address = ", ".join(addr_parts[:-2])
        else:
            address = address_full
            city = ""
            state = "MI"
            zip_code = ""
            
        phone = utils.clean_phone_number(phone)
        co_key = f"{business_name.upper()} | {city.upper()}"
        
        if co_key not in unique_companies:
            unique_companies[co_key] = {
                "name": business_name,
                "address": address_full,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "county": county,
                "phone": phone,
                "types": [contractor_type],
                "licenses": [f"{contractor_type} #{license_num} ({contractor_name})"]
            }
        else:
            if contractor_type not in unique_companies[co_key]["types"]:
                unique_companies[co_key]["types"].append(contractor_type)
            unique_companies[co_key]["licenses"].append(f"{contractor_type} #{license_num} ({contractor_name})")
            
    print(f"[+] Deduplicated into {len(unique_companies)} unique service companies.")
    
    inserted_count = 0
    for key, co in unique_companies.items():
        slug = utils.slugify(co["name"])
        c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (slug,))
        if c.fetchone():
            slug = f"{slug}-{utils.slugify(co['city'])}"
            
        license_str = ", ".join(co["licenses"])
        
        c.execute('''
            INSERT OR IGNORE INTO installers_haulers 
            (name, slug, address, city, state, zip_code, county, phone_number, pumper_certification_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            co["name"], slug, co["address"], co["city"], co["state"], co["zip_code"],
            co["county"], co["phone"], license_str
        ))
        inserted_count += 1
        
    conn.commit()
    conn.close()
    print(f"[+] Successfully saved {inserted_count} records to {db_path}!")

def main():
    print("[*] Starting Michigan Water Well Driller Scraper")
    
    records = asyncio.run(scrape_powerbi_grid())
    print(f"[+] Scraped {len(records)} raw grid records.")
    
    parse_and_save(records)

if __name__ == "__main__":
    main()
