import os
import asyncio
import sys
from playwright.async_api import async_playwright

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import utils

async def main():
    # Dynamic destination path resolved relative to workspace root
    pdf_dest = utils.resolve_path("cache/ohio_registered_pws_contractors.pdf")
    os.makedirs(os.path.dirname(pdf_dest), exist_ok=True)
    
    print("[*] Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        url = "https://odh.ohio.gov/know-our-programs/private-water-systems-program/media/list-regpwsc-ohio"
        print(f"[*] Navigating to {url}...")
        await page.goto(url, wait_until="networkidle", timeout=45000)
        
        print("[*] Page loaded. Searching for PDF link...")
        
        link_selector = 'a[href*=".pdf"]'
        download_link = page.locator(link_selector).first
        
        count = await download_link.count()
        if count == 0:
            print("[-] No PDF link found using locator. Searching DOM...")
            links = await page.query_selector_all("a")
            href = None
            for link in links:
                href_attr = await link.get_attribute("href")
                if href_attr and ".pdf" in href_attr.lower():
                    href = href_attr
                    break
        else:
            href = await download_link.get_attribute("href")
            
        if not href:
            print("[-] PDF URL not found. Exiting.")
            await browser.close()
            return
            
        print(f"[+] Found relative PDF path: {href}")
        full_url = href
        if href.startswith("/"):
            full_url = "https://odh.ohio.gov" + href
            
        print(f"[*] Requesting PDF directly via browser API context: {full_url}...")
        
        response = await page.request.get(full_url, timeout=60000)
        print(f"[+] Response status: {response.status}")
        
        if response.status == 200:
            body = await response.body()
            with open(pdf_dest, "wb") as f:
                f.write(body)
            print(f"[+] Successfully saved PDF to {pdf_dest}")
            print(f"    - File size: {os.path.getsize(pdf_dest)} bytes")
        else:
            print(f"[-] Failed to download PDF. Status: {response.status}")
            
        await browser.close()
        print("[*] Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
