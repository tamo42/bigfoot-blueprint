from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to https://ehs.ncpublichealth.com...")
            page.goto('https://ehs.ncpublichealth.com', timeout=30000)
            print("Title:", page.title())
            page.screenshot(path='nc_dhhs_screenshot.png')
            print("Screenshot saved to nc_dhhs_screenshot.png")
            print("Content snippet:", page.content()[:1000])
        except Exception as e:
            print("Error visiting ehs.ncpublichealth.com:", e)
        
        try:
            print("\nNavigating to https://www.ncwelldriller.org/web/eh/find-contractor...")
            page.goto('https://www.ncwelldriller.org/web/eh/find-contractor', timeout=30000)
            print("Title:", page.title())
            page.screenshot(path='nc_welldriller_screenshot.png')
            print("Screenshot saved to nc_welldriller_screenshot.png")
            print("Content snippet:", page.content()[:1000])
        except Exception as e:
            print("Error visiting www.ncwelldriller.org:", e)
            
        browser.close()

if __name__ == '__main__':
    run()
