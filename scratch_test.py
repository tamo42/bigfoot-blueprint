from playwright.sync_api import sync_playwright

def test_bing():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        firm_name = "Host Law"
        city = "Atlanta"
        
        url = f"https://www.bing.com/search?q=site:fntic.com+OR+site:firstam.com+OR+site:stewart.com+\"{firm_name}\""
        print("Searching Bing:", url)
        
        page.goto(url)
        page.wait_for_selector('#b_results')
        
        # Get the text of the results
        results_text = page.locator('#b_results').inner_text()
        print("Results:\n", results_text[:1000])
        
        browser.close()

if __name__ == "__main__":
    test_bing()
