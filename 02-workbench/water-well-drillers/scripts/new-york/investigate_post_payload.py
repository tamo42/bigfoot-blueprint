from playwright.sync_api import sync_playwright
import json

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_request(request):
            if "screenservices" in request.url and "GetWaterwellDrillingCompaniesByName" in request.url and request.method == "POST":
                with open("ny_post_payload.json", "w") as f:
                    f.write(request.post_data)
                    
        page.on("request", handle_request)
        
        print("Navigating to NY DEC Water Well Contractor Search...")
        page.goto("https://appfactory.dec.ny.gov/WaterWell/Contractor_Search", wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        print("Clicking Tab 2 (Search By Business Name)...")
        page.click("text=Search By Business Name")
        page.wait_for_timeout(1000)
        
        print("Searching with empty business name...")
        page.fill("#Input_BusinessName4", "a")
        page.wait_for_timeout(500)
        
        # Click search
        page.click("button:has-text('Search Contractors') >> nth=1")
        page.wait_for_timeout(4000) # Wait for response to be handled
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
