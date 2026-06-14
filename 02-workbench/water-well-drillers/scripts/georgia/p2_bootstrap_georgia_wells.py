import os
import re
import json
import sqlite3
import time
import requests
import pypdf
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils
import p3_schema as schema

# Load API Key
api_key = utils.load_env_api_key()
if not api_key:
    print("[-] Error: GOOGLE_PLACES_API_KEY not found in .env")
    exit(1)

# Dynamic paths
cache_dir = utils.resolve_path("cache")
db_path = utils.get_db_path("georgia")
places_cache_path = utils.get_places_cache_path()

# Load Places API Cache
places_cache = {}
if os.path.exists(places_cache_path):
    try:
        with open(places_cache_path, 'r', encoding='utf-8') as f:
            places_cache = json.load(f)
        print(f"[+] Loaded {len(places_cache)} cached Places API responses.")
    except Exception as e:
        print(f"[-] Error loading Places cache: {e}")

def save_places_cache():
    try:
        with open(places_cache_path, 'w', encoding='utf-8') as f:
            json.dump(places_cache, f, indent=2)
    except Exception as e:
        print(f"[-] Error saving Places cache: {e}")

def parse_epd_pdf(pdf_filename, contractor_type):
    pdf_path = os.path.join(cache_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        print(f"[-] Error: File not found: {pdf_path}")
        return []
        
    reader = pypdf.PdfReader(pdf_path)
    records = []
    
    for page in reader.pages:
        text_layout = page.extract_text(extraction_mode="layout")
        lines = text_layout.split('\n')
        
        for line in lines:
            line_str = line.strip()
            # Skip headers
            if not line_str or "License" in line_str or "Last Name" in line_str or "List revised" in line_str or "expire" in line_str or "Number" in line_str or "Certificate" in line_str:
                continue
                
            # Split by double spaces or more
            parts = re.split(r'\s{2,}', line_str)
            if len(parts) < 5:
                continue
                
            # License number must be the first part
            license_num = parts[0]
            if not license_num.isdigit():
                continue
                
            # Parse from the right
            zip_code = parts[-1]
            state = parts[-2]
            city = parts[-3]
            
            # The rest of the parts are: name, company, address
            leftover = parts[1:-3]
            if not leftover:
                continue
                
            # Heuristic to handle split address parts
            address_parts = [leftover[-1]]
            leftover = leftover[:-1]
            
            if leftover and (address_parts[0].isdigit() or len(address_parts[0]) <= 5 or address_parts[0].startswith('#')):
                # Merge address
                address_parts.insert(0, leftover[-1])
                leftover = leftover[:-1]
                
            address = " ".join(address_parts)
            
            # The remaining parts are: name elements and company name in 'leftover'
            company = ""
            if leftover:
                company = leftover[-1]
                leftover = leftover[:-1]
                
            name_parts = leftover
            last_name = name_parts[0] if len(name_parts) > 0 else ""
            first_name = name_parts[1] if len(name_parts) > 1 else ""
            
            records.append({
                "license_num": license_num,
                "last_name": last_name,
                "first_name": first_name,
                "company_name": company if company else f"{first_name} {last_name} Well Drilling".strip(),
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "contractor_type": contractor_type
            })
            
    return records

def main():
    print("[*] Parsing Georgia EPD contractor PDFs...")
    well_drillers = parse_epd_pdf("georgia_licensed_water_well_contractors.pdf", "well_driller")
    pump_installers = parse_epd_pdf("georgia_certified_pump_contractors.pdf", "pump_installer")
    bonded_drillers = parse_epd_pdf("georgia_bonded_drilling_contractors_pg_pe.pdf", "bonded_driller")
    
    print(f"  [+] Parsed {len(well_drillers)} well drillers.")
    print(f"  [+] Parsed {len(pump_installers)} pump installers.")
    print(f"  [+] Parsed {len(bonded_drillers)} bonded drillers.")
    
    # Combine and Deduplicate
    all_contractors = well_drillers + pump_installers + bonded_drillers
    unique_companies = {}
    
    for c in all_contractors:
        co_name = re.sub(r'[^a-zA-Z0-9\s\-\.,&]', '', c["company_name"]).strip().upper()
        city = c["city"].strip().upper()
        key = f"{co_name} | {city}"
        
        if key not in unique_companies:
            unique_companies[key] = {
                "name": c["company_name"],
                "city": c["city"],
                "state": c["state"],
                "zip_code": c["zip_code"],
                "address": f"{c['address']}, {c['city']}, {c['state']} {c['zip_code']}",
                "types": [c["contractor_type"]],
                "licenses": [f"{c['contractor_type'].upper()} #{c['license_num']}"]
            }
        else:
            if c["contractor_type"] not in unique_companies[key]["types"]:
                unique_companies[key]["types"].append(c["contractor_type"])
            unique_companies[key]["licenses"].append(f"{c['contractor_type'].upper()} #{c['license_num']}")
            
    print(f"[+] Deduplicated into {len(unique_companies)} unique service companies.")
    
    # Enrich via Google Places API (with Local Cache)
    enriched_count = 0
    places_queries_made = 0
    
    for key, co in unique_companies.items():
        cache_key = f"{co['name'].lower()} | {co['city'].lower()}"
        co["place_id"] = None
        co["website_url"] = None
        co["latitude"] = None
        co["longitude"] = None
        co["google_rating"] = 0
        co["google_review_count"] = 0
        co["reviews_json"] = None
        
        if cache_key in places_cache:
            res = places_cache[cache_key]
        else:
            # Respect $10 budget constraint
            if places_queries_made >= 280:
                res = {}
            else:
                search_query = f"{co['name']} {co['city']} Georgia"
                print(f"[*] Querying Places API: '{search_query}'...")
                
                find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                find_params = {
                    'input': search_query,
                    'inputtype': 'textquery',
                    'fields': 'place_id',
                    'key': api_key
                }
                
                res = {
                    "place_id": None,
                    "website_url": None,
                    "latitude": None,
                    "longitude": None,
                    "rating": None,
                    "reviews_count": None,
                    "reviews_json": None
                }
                
                try:
                    find_res = requests.get(find_url, params=find_params, timeout=10).json()
                    places_queries_made += 1
                    
                    if find_res.get('status') == 'OK' and len(find_res.get('candidates', [])) > 0:
                        place_id = find_res['candidates'][0]['place_id']
                        res["place_id"] = place_id
                        
                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {
                            'place_id': place_id,
                            'fields': 'website,geometry,rating,user_ratings_total,reviews',
                            'key': api_key
                        }
                        det_res = requests.get(details_url, params=details_params, timeout=10).json()
                        places_queries_made += 1
                        
                        if det_res.get('status') == 'OK':
                            result = det_res.get('result', {})
                            res["website_url"] = result.get('website')
                            res["rating"] = result.get('rating')
                            res["reviews_count"] = result.get('user_ratings_total')
                            
                            if result.get('geometry') and result['geometry'].get('location'):
                                res["latitude"] = result['geometry']['location'].get('lat')
                                res["longitude"] = result['geometry']['location'].get('lng')
                                
                            reviews = result.get('reviews', [])
                            if reviews:
                                res["reviews_json"] = json.dumps([r.get('text') for r in reviews if r.get('text')])
                                
                    places_cache[cache_key] = res
                    save_places_cache()
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"  [-] Error querying Places API for {co['name']}: {e}")
                    
        if res.get("place_id"):
            co["place_id"] = res.get("place_id")
            co["website_url"] = res.get("website_url")
            co["latitude"] = res.get("latitude")
            co["longitude"] = res.get("longitude")
            co["google_rating"] = res.get("rating") if res.get("rating") else 0
            co["google_review_count"] = res.get("reviews_count") if res.get("reviews_count") else 0
            co["reviews_json"] = res.get("reviews_json")
            enriched_count += 1
            
    print(f"[+] Google Places enrichment completed. Enriched {enriched_count}/{len(unique_companies)} companies.")
    
    # Save to SQLite using schema manager
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    schema.initialize_database(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    inserted_count = 0
    for key, co in unique_companies.items():
        slug = utils.slugify(co["name"])
        c.execute("SELECT id FROM installers_haulers WHERE slug = ?", (slug,))
        if c.fetchone():
            slug = f"{slug}-{utils.slugify(co['city'])}"
            
        license_str = ", ".join(co["licenses"])
        
        c.execute('''
            INSERT OR IGNORE INTO installers_haulers 
            (name, slug, address, city, state, zip_code, website_url, google_rating, google_review_count, manual_lat, manual_lng, pumper_certification_level, google_place_id, reviews_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            co["name"], slug, co["address"], co["city"], co["state"], co["zip_code"], 
            co["website_url"], co["google_rating"], co["google_review_count"], co["latitude"], co["longitude"],
            license_str, co["place_id"], co["reviews_json"]
        ))
        inserted_count += 1
        
    conn.commit()
    conn.close()
    print(f"[+] Successfully saved {inserted_count} records to {db_path}!")

if __name__ == "__main__":
    main()
