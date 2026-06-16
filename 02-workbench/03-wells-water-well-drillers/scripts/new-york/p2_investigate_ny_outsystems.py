from playwright.sync_api import sync_playwright
import json

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    responses = []

    def handle_response(response):
        if "screenservices" in response.url and response.request.method == "POST":
            try:
                data = response.json()
                responses.append({"url": response.url, "data": data})
            except Exception as e:
                pass

    page.on("response", handle_response)
    print("Navigating to OutSystems app...")
    page.goto("https://appfactory.dec.ny.gov/WaterWell/Contractor_Search", wait_until="networkidle")
    
    page.wait_for_timeout(2000)
    
    print("Clicking Tab 2 (Search By Business Name)...")
    # The tab has text "Search By Business Name"
    page.click("text=Search By Business Name")
    page.wait_for_timeout(1000)
    
    print("Typing in business name 'A'...")
    page.fill("#Input_BusinessName4", "a")
    page.wait_for_timeout(1000)
    
    print("Clicking Search Contractors button...")
    page.click("button:has-text('Search Contractors') >> nth=1") # 2nd button
    
    page.wait_for_timeout(5000)
    page.screenshot(path="../../scratch/ny_search_page.png", full_page=True)
    print("Screenshot saved to scratch/ny_search_page.png")
    
    # Dump HTML to look for button names
    with open("ny_search_page.html", "w", encoding="utf-8") as f:
        f.write(page.content())
        
    print(f"Captured {len(responses)} OutSystems responses.")
    with open("ny_outsystems_responses3.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
