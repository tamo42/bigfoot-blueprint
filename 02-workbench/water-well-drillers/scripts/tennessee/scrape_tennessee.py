import os
import asyncio
import sys
from playwright.async_api import async_playwright

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import utils

async def main():
    print("[*] Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        url = "https://dataviewers.tdec.tn.gov/dataviewers/f?p=2005:39918"
        print(f"[*] Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"[+] Page Title: {title}")
        
        # Take a screenshot to verify load (path resolved relative to workspace root)
        screenshot_path = utils.resolve_path("02-workbench/water-well-drillers/tdec_screenshot.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        await page.screenshot(path=screenshot_path)
        print(f"[+] Screenshot saved to {screenshot_path}")
        
        print("\n[*] Searching for interactive elements...")
        
        buttons = await page.query_selector_all("button")
        print(f"Found {len(buttons)} button elements:")
        for idx, btn in enumerate(buttons[:15]):
            text = await btn.inner_text()
            btn_id = await btn.get_attribute("id")
            btn_class = await btn.get_attribute("class")
            print(f"  {idx+1}. ID: {btn_id} | Class: {btn_class} | Text: '{text.strip()}'")
            
        links = await page.query_selector_all("a")
        print(f"\nFound {len(links)} link elements. Links with relevant text:")
        relevant_links_count = 0
        for link in links:
            text = await link.inner_text()
            href = await link.get_attribute("href")
            text_lower = text.lower()
            if any(kw in text_lower for kw in ["download", "export", "actions", "csv", "excel", "report"]):
                relevant_links_count += 1
                link_id = await link.get_attribute("id")
                print(f"  * ID: {link_id} | Text: '{text.strip()}' | Href: '{href}'")
        if relevant_links_count == 0:
            print("  (No links containing download/export/actions/csv/excel/report keywords found)")
            
        html_content = await page.content()
        is_apex = "apex" in html_content.lower()
        print(f"\n[+] Is Oracle APEX page? {is_apex}")
        
        await browser.close()
        print("[*] Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
