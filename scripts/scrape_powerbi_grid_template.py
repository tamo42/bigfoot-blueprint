import asyncio
from playwright.async_api import async_playwright

# ==============================================================================
# POWER BI GRID SCRAPER TEMPLATE
# ==============================================================================
# This is a generic Playwright scraper designed to extract data from 
# virtualized PowerBI dashboards (e.g., app.powerbigov.us).
# 
# Usage:
# 1. Replace POWERBI_EMBED_URL with the target dashboard URL.
# 2. Adjust the wait_for_timeout() delays based on the dashboard's load speed.
# 3. Update the parser logic in main() to map the extracted text array into
#    the appropriate database schema for your Bigfoot Blueprint site.
# ==============================================================================

POWERBI_EMBED_URL = 'https://app.powerbigov.us/view?r=...'

async def scrape_powerbi_grid():
    records_set = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"[*] Navigating to PowerBI page...")
        await page.goto(POWERBI_EMBED_URL, wait_until='networkidle')
        
        print("[*] Waiting for dashboard to load...")
        # Note: PowerBI can take a long time to render the initial visual-container
        await page.wait_for_timeout(10000) 
        
        previous_len = 0
        scroll_attempts = 0
        
        # PowerBI grids only render the rows currently visible in the viewport.
        # We must scroll the grid and read the DOM repeatedly until no new records appear.
        while scroll_attempts < 20: 
            rows = await page.query_selector_all('div[role="row"]')
            if not rows:
                break
                
            for r in rows:
                text = await r.inner_text()
                # Exclude header rows or blank lines
                if text.strip() and "Select Row" not in text:
                    records_set.add(text.strip())
            
            if len(records_set) > previous_len:
                print(f"[+] Found {len(records_set)} records so far...")
                previous_len = len(records_set)
                scroll_attempts = 0
            else:
                scroll_attempts += 1
                
            # Scroll the last visible row into view to trigger PowerBI's lazy loading
            try:
                await rows[-1].scroll_into_view_if_needed()
                await page.mouse.wheel(0, 500)
            except Exception as e:
                pass
                
            # Wait for the network to fetch the next chunk of rows
            await page.wait_for_timeout(1000)
            
        await browser.close()
        
    return list(records_set)

def main():
    print("[*] Starting PowerBI Grid Scraper")
    
    records = asyncio.run(scrape_powerbi_grid())
    print(f"[+] Scraped {len(records)} raw grid records.")
    
    # Example of parsing the newline-delimited grid cell texts:
    for raw in records[:5]: # Show a sample
        lines = [line.strip() for line in raw.split('\n') if line.strip()]
        print(f"Sample Row Data: {lines}")
        
        # TODO: Implement Bigfoot Blueprint schema parsing and SQLite DB insertion here.

if __name__ == "__main__":
    main()
