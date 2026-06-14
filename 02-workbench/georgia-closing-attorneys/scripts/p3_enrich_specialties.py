import sqlite3
import json
import os
import re
import argparse

# Database and Cache Configuration
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "data", "directory.sqlite")
CACHE_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "cache", "crawled_text", "georgia-closing-attorneys")

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

PAYMENT_METHODS_MAP = {
    "ZOCCAM": [r"zoccam"],
    "Earnnest App": [r"earnnest"],
    "Wire Transfer": [r"wire transfer", r"wiring instructions"],
    "Cashier's Check": [r"cashier's check", r"certified check", r"cashiers check"]
}

TRUST_SIGNALS_MAP = {
    "wire_fraud_protocol": [r"wire fraud", r"fraud warning", r"call before wiring", r"never email wiring"],
    "wheelchair_accessible": [r"wheelchair accessible", r"handicap accessible", r"ada compliant"],
    "parking_available": [r"free parking", r"parking available", r"parking lot", r"validated parking"],
    "eo_insurance_verified": [r"e&o insurance", r"errors and omissions", r"errors & omissions", r"liability insurance"]
}

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

def scan_text_for_specialties(text, compiled_wholesale, compiled_creative, compiled_land, compiled_title, compiled_langs, compiled_payments, compiled_trust):
    results = {
        "wholesale": 0,
        "creative_finance": 0,
        "land_deals": 0,
        "title_resolution": 0,
        "languages": ["English"],
        "payment_methods": [],
        "trust_signals": {
            "wire_fraud_protocol": False,
            "wheelchair_accessible": False,
            "parking_available": False,
            "eo_insurance_verified": False
        }
    }
    
    if not text:
        return results
        
    results["wholesale"] = check_keywords(text, compiled_wholesale)
    results["creative_finance"] = check_keywords(text, compiled_creative)
    results["land_deals"] = check_keywords(text, compiled_land)
    results["title_resolution"] = check_keywords(text, compiled_title)
    
    results["languages"] = detect_languages(text, compiled_langs)
    
    for method, patterns in compiled_payments.items():
        if check_keywords(text, patterns):
            results["payment_methods"].append(method)
            
    for signal, patterns in compiled_trust.items():
        if check_keywords(text, patterns):
            results["trust_signals"][signal] = True
    
    found_specialties = []
    if results["wholesale"]: found_specialties.append("Wholesale")
    if results["creative_finance"]: found_specialties.append("Creative Finance")
    if results["land_deals"]: found_specialties.append("Land Deals")
    if results["title_resolution"]: found_specialties.append("Title Resolution")
    
    if found_specialties:
        print(f"      [+] Found Specialties: {', '.join(found_specialties)}")
    if len(results["languages"]) > 1:
        print(f"      [+] Found Languages: {', '.join(results['languages'])}")
        
    return results

def run_enrichment(limit=50):
    print("=========================================================")
    print(f"Georgia Closing Attorneys - Offline Specialty Enrichment")
    print("=========================================================")
    print(f"Targeting batch limit: {limit}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    compiled_wholesale = compile_regex(KEYWORDS_WHOLESALE)
    compiled_creative = compile_regex(KEYWORDS_CREATIVE_FINANCE)
    compiled_land = compile_regex(KEYWORDS_LAND_DEALS)
    compiled_title = compile_regex(KEYWORDS_TITLE_RESOLUTION)
    
    compiled_langs = {}
    for lang, kws in LANGUAGES_MAP.items():
        compiled_langs[lang] = compile_regex(kws)
        
    compiled_payments = {}
    for method, kws in PAYMENT_METHODS_MAP.items():
        compiled_payments[method] = compile_regex(kws)
        
    compiled_trust = {}
    for signal, kws in TRUST_SIGNALS_MAP.items():
        compiled_trust[signal] = compile_regex(kws)
    
    c.execute('''
        SELECT id, first_name, last_name, firm_name, city 
        FROM attorneys 
        WHERE specialties_crawled = 0 AND website_url IS NOT NULL AND website_url != 'NOT_FOUND'
        LIMIT ?
    ''', (limit,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending records to enrich in this batch.")
        conn.close()
        return
        
    print(f"Found {len(records)} records to process.")
    
    for idx, row in enumerate(records):
        attorney_id = row['id']
        first_name = row['first_name']
        last_name = row['last_name']
        firm_name = row['firm_name'] or ""
        city = row['city']
        
        display_name = firm_name if firm_name else f"{first_name} {last_name}"
        print(f"\n[{idx+1}/{len(records)}] Processing ID {attorney_id}: {display_name} ({city})")
        
        cache_file = os.path.join(CACHE_DIR, f"{attorney_id}.txt")
        failed_file = os.path.join(CACHE_DIR, f"{attorney_id}.failed")
        
        if os.path.exists(failed_file):
            print(f"      [-] Crawl failed for this site previously. Marking as scanned.")
            res = scan_text_for_specialties("", compiled_wholesale, compiled_creative, compiled_land, compiled_title, compiled_langs, compiled_payments, compiled_trust)
        elif os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                content = f.read()
            res = scan_text_for_specialties(
                content, 
                compiled_wholesale, compiled_creative, compiled_land, compiled_title, 
                compiled_langs, compiled_payments, compiled_trust
            )
        else:
            print(f"      [-] No cache file found. You must run p3_crawl_websites.py first. Skipping.")
            continue
            
        c.execute('''
            UPDATE attorneys
            SET specialty_wholesale = ?,
                specialty_creative_finance = ?,
                specialty_land_deals = ?,
                specialty_title_resolution = ?,
                languages_spoken = ?,
                trust_signals_json = ?,
                accepted_payment_methods = ?,
                specialties_crawled = 1
            WHERE id = ?
        ''', (
            res["wholesale"],
            res["creative_finance"],
            res["land_deals"],
            res["title_resolution"],
            json.dumps(res["languages"]),
            json.dumps(res["trust_signals"]),
            json.dumps(res["payment_methods"]),
            attorney_id
        ))
        
        conn.commit()
        print(f"  [+] Saved details and marked ID {attorney_id} as specialties_crawled.")
        
    conn.close()
    print("\n=========================================================")
    print("Specialty Offline Enrichment Batch Complete!")
    print("=========================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich attorney records with specialties offline from cache.")
    parser.add_argument("--limit", type=int, default=50, help="Number of records to process (default: 50)")
    args = parser.parse_args()
    
    run_enrichment(limit=args.limit)
