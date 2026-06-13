import sqlite3
import random
import time
import json
import os
import re
import argparse
from playwright.sync_api import sync_playwright

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/directory.sqlite')

# Keyword Lists
KEYWORDS_WHOLESALE = [
    r"double closing", r"double close",
    r"simultaneous closing", r"simultaneous close",
    r"wholesale", r"wholesal",
    r"assignment of contract", r"assign contract",
    r"transactional funding",
    r"investor-friendly", r"investor friendly"
]

KEYWORDS_CREATIVE_FINANCE = [
    r"subject-to", r"subject to mortgage", r"subject to existing mortgage", r"subject to the existing mortgage",
    r"seller finance", r"seller financing",
    r"owner finance", r"owner financing",
    r"wrap mortgage", r"wrap-around mortgage", r"wrap around mortgage",
    r"creative finance", r"creative financing"
]

KEYWORDS_LAND_DEALS = [
    r"vacant land", r"raw land", r"undeveloped land",
    r"acreage", r"large tract", r"land contract",
    r"agricultural land", r"farm land"
]

KEYWORDS_TITLE_RESOLUTION = [
    r"quiet title",
    r"heir property", r"heirship",
    r"title defect", r"clearing title", r"clear title",
    r"probate resolution", r"probate property",
    r"lien clearance", r"lien resolution", r"resolving liens", r"judgment lien", r"tax lien",
    r"easement issue", r"boundary dispute", r"encroachment"
]

LANGUAGES_MAP = {
    "Spanish": [r"spanish", r"español", r"espanol", r"habla español", r"habla espanol", r"bilingual"],
    "Korean": [r"korean", r"한국어"],
    "Vietnamese": [r"vietnamese", r"tiếng việt"],
    "Chinese": [r"mandarin", r"cantonese", r"chinese", r"中文"]
}

def human_delay(min_sec=2.0, max_sec=5.0):
    """Introduces a randomized delay 'jiggle' to mimic human interaction."""
    delay = random.uniform(min_sec, max_sec)
    print(f"[*] Human-mimicking delay: sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

def compile_regex(keywords):
    return [re.compile(kw, re.IGNORECASE) for kw in keywords]

def check_keywords(text, compiled_patterns):
    for pattern in compiled_patterns:
        if pattern.search(text):
            return 1
    return 0

def detect_languages(text, compiled_languages):
    langs = ["English"]
    for lang, patterns in compiled_languages.items():
        for pattern in patterns:
            if pattern.search(text):
                langs.append(lang)
                break
    return list(set(langs))

def scrape_website_for_specialties(page, url, compiled_wholesale, compiled_creative, compiled_land, compiled_title, compiled_langs):
    """
    Visits the firm's website homepage and extracts content to scan for specialties and languages.
    """
    results = {
        "wholesale": 0,
        "creative_finance": 0,
        "land_deals": 0,
        "title_resolution": 0,
        "languages": ["English"]
    }
    
    if not url or url == 'NOT_FOUND':
        print("      [-] No valid website URL provided.")
        return results
        
    if not url.startswith('http'):
        url = 'https://' + url
        
    print(f"  [*] Crawling website: {url}...")
    try:
        # 15 second timeout to avoid hanging on dead sites
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        
        title = page.title()
        # Grab text of the whole page body
        body_text = page.locator('body').inner_text()
        print(f"      [+] Loaded page: '{title}' (Body text length: {len(body_text)})")
        
        # Run matches
        results["wholesale"] = check_keywords(body_text, compiled_wholesale)
        results["creative_finance"] = check_keywords(body_text, compiled_creative)
        results["land_deals"] = check_keywords(body_text, compiled_land)
        results["title_resolution"] = check_keywords(body_text, compiled_title)
        results["languages"] = detect_languages(body_text, compiled_langs)
        
        # Log findings
        found_specialties = []
        if results["wholesale"]: found_specialties.append("Wholesale")
        if results["creative_finance"]: found_specialties.append("Creative Finance")
        if results["land_deals"]: found_specialties.append("Land Deals")
        if results["title_resolution"]: found_specialties.append("Title Resolution")
        
        if found_specialties:
            print(f"      [+] Found Specialties: {', '.join(found_specialties)}")
        if len(results["languages"]) > 1:
            print(f"      [+] Found Languages: {', '.join(results['languages'])}")
            
    except Exception as e:
        print(f"      [!] Website scrape error: {e}")
        
    return results

def run_enrichment(limit=50):
    print("=========================================================")
    print(f"Georgia Closing Attorneys - Specialty Crawl Enrichment")
    print(f"=========================================================")
    print(f"Targeting batch limit: {limit}")
    print(f"Database path: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Compile regexes once
    compiled_wholesale = compile_regex(KEYWORDS_WHOLESALE)
    compiled_creative = compile_regex(KEYWORDS_CREATIVE_FINANCE)
    compiled_land = compile_regex(KEYWORDS_LAND_DEALS)
    compiled_title = compile_regex(KEYWORDS_TITLE_RESOLUTION)
    
    compiled_langs = {}
    for lang, kws in LANGUAGES_MAP.items():
        compiled_langs[lang] = compile_regex(kws)
    
    # Fetch un-crawled records
    c.execute('''
        SELECT id, first_name, last_name, firm_name, city, website_url 
        FROM attorneys 
        WHERE specialties_crawled = 0 AND website_url IS NOT NULL AND website_url != 'NOT_FOUND'
        LIMIT ?
    ''', (limit,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending records with websites found for specialty crawl.")
        return
        
    print(f"Found {len(records)} records to enrich in this batch.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for idx, row in enumerate(records):
            attorney_id = row['id']
            first_name = row['first_name']
            last_name = row['last_name']
            firm_name = row['firm_name'] or ""
            city = row['city']
            website_url = row['website_url']
            
            display_name = firm_name if firm_name else f"{first_name} {last_name}"
            print(f"\n[{idx+1}/{len(records)}] Processing ID {attorney_id}: {display_name} ({city})")
            
            res = scrape_website_for_specialties(
                page, website_url, 
                compiled_wholesale, compiled_creative, compiled_land, compiled_title, 
                compiled_langs
            )
            
            # Save results back to database and mark as crawled
            c.execute('''
                UPDATE attorneys
                SET specialty_wholesale = ?,
                    specialty_creative_finance = ?,
                    specialty_land_deals = ?,
                    specialty_title_resolution = ?,
                    languages_spoken = ?,
                    specialties_crawled = 1
                WHERE id = ?
            ''', (
                res["wholesale"],
                res["creative_finance"],
                res["land_deals"],
                res["title_resolution"],
                json.dumps(res["languages"]),
                attorney_id
            ))
            
            conn.commit()
            print(f"  [+] Saved details and marked ID {attorney_id} as specialties_crawled.")
            
            # Inter-record delay to avoid triggering bot blocks
            human_delay(2.0, 4.5)
            
        browser.close()
        
    conn.close()
    print("\n=========================================================")
    print("Specialty Crawl Ingestion Batch Complete!")
    print("=========================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich attorney records with website scraped specialties.")
    parser.add_argument("--limit", type=int, default=50, help="Number of records to process in this batch (default: 50)")
    args = parser.parse_args()
    
    run_enrichment(limit=args.limit)
