import os
import sys
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        url = "https://permitting.sjrwmd.com/nwep/#/srch/(topoutlet:contractor)"
        print(f"[*] Navigating to {url}...")
        page.goto(url, timeout=60000)
        
        print("[*] Waiting for Search button...")
        # Wait for the search button
        page.wait_for_selector("button:has-text('Search')", timeout=30000)
        
        print("[*] Clicking Search...")
        page.click("button:has-text('Search')")
        
        print("[*] Waiting for Export Results button...")
        # Wait for the results to load and the export button to become active
        page.wait_for_selector("button:has-text('Export Results')", timeout=30000)
        
        print("[*] Triggering download...")
        with page.expect_download() as download_info:
            page.click("button:has-text('Export Results')")
            
        download = download_info.value
        cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cache"))
        os.makedirs(cache_dir, exist_ok=True)
        
        # Determine output filename (default to .xlsx)
        suggested_filename = download.suggested_filename
        extension = os.path.splitext(suggested_filename)[1] if suggested_filename else ".xlsx"
        
        save_path = os.path.join(cache_dir, f"florida_statewide{extension}")
        download.save_as(save_path)
        print(f"[+] Download complete! Saved to {save_path}")
        
        browser.close()

if __name__ == "__main__":
    main()
