import os
import sys
import json
import sqlite3
import argparse
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import p3_utils as utils
import p3_schema as schema

# State abbreviation to folder mapping
STATE_TO_FOLDER = {
    "GA": "georgia",
    "MI": "michigan",
    "NY": "new_york",
    "NC": "north_carolina",
    "OH": "ohio",
    "PA": "pennsylvania",
    "TX": "texas",
    "VA": "virginia"
}

# The canonical 10 questions for Water Well Drillers directory
CANONICAL_QUESTIONS = [
    "What are the emergency response hours, procedures, and pricing for urgent well or pump failures?",
    "How does the permitting and registration process work for drilling or modifying a water well in this area?",
    "What are the mandatory sanitary setback distances required between a water well and septic tanks or sewer lines?",
    "What are the typical drilling depths and aquifer conditions for water wells in this region?",
    "What types of water quality testing and filtration systems are recommended for local wells?",
    "What warranties and service guarantees are provided for new well pump and tank installations?",
    "What rehabilitation or deepening options are available if an existing water well runs dry or has low yield?",
    "Do they offer solar-powered or off-grid well pump installation and battery backup services?",
    "What is the legal process and requirement for well abandonment or decommissioning in this state?",
    "What payment terms, credit cards, or financing options are available for major drilling projects?"
]

def load_gemini_api_key():
    """
    Finds and loads the Gemini API key from environment variables or .env at root.
    """
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    
    env_path = utils.resolve_path(".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    return line.split('=', 1)[1].strip()
                elif line.startswith('GOOGLE_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return None

def init_gemini_client(api_key):
    """
    Dynamically attempts to import google-genai or google-generativeai and returns a wrapper function.
    """
    # 1. Try modern google-genai SDK
    try:
        from google import genai
        from google.genai import types
        print("[+] Successfully imported google-genai (modern SDK).")
        client = genai.Client(api_key=api_key)
        
        def call_gemini_modern(prompt, response_schema):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)
            
        return call_gemini_modern
    except ImportError:
        pass
        
    # 2. Try legacy google-generativeai SDK
    try:
        import google.generativeai as genai_legacy
        print("[+] Successfully imported google-generativeai (legacy SDK).")
        genai_legacy.configure(api_key=api_key)
        
        def call_gemini_legacy(prompt, response_schema):
            model = genai_legacy.GenerativeModel(
                model_name='gemini-2.5-flash',
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                    "temperature": 0.1
                }
            )
            response = model.generate_content(prompt)
            return json.loads(response.text)
            
        return call_gemini_legacy
    except ImportError:
        pass
        
    print("[-] Error: Neither google-genai nor google-generativeai python packages are installed.")
    sys.exit(1)

def get_response_schema(num_qa):
    """
    Generates OpenAPI 3.0 compatible JSON schema for Gemini structured output.
    """
    properties = {
        "emergency_repair_247": {"type": "integer", "description": "1 if they offer 24/7 or emergency pump repair / service, otherwise 0"},
        "emergency_response_time": {"type": "string", "description": "Emergency response window if mentioned (e.g. 'Within 2 hours', 'Same day'), otherwise empty string"},
        "emergency_services_offered": {"type": "string", "description": "Summary of emergency services offered, otherwise empty string"},
        "pressure_tank_services": {"type": "integer", "description": "1 if they service pressure switches, bladder tanks, or well tanks, otherwise 0"},
        "water_testing_offered": {"type": "integer", "description": "1 if they offer well water quality testing, otherwise 0"},
        "water_treatment_installed": {"type": "string", "description": "Summary of water treatment systems installed (softeners, filtration, UV, RO), otherwise empty string"},
        "handles_new_permits": {"type": "integer", "description": "1 if they handle county/local permits for drilling new wells, otherwise 0"},
        "listing_content": {"type": "string", "description": "Detailed 200-400 words HTML description about the company. Use HTML tags (<p>, <strong>, <ul>, <li>). Do not use markdown."},
        "speakable_what_you_find": {"type": "string", "description": "1-2 sentence spoken summary of what services this contractor offers."},
        "speakable_listing_details": {"type": "string", "description": "1-2 sentence spoken summary of licensing, emergency hours, and contact info."},
        "speakable_quick_facts": {"type": "string", "description": "1-2 sentence spoken summary of primary specialties and service area."},
        "quickfact_best_for": {"type": "string", "description": "Short phrase describing what they are best for."},
        "quickfact_primary_services": {"type": "string", "description": "Comma-separated list of 3-5 primary services."},
        "quickfact_pricing_guide": {"type": "string", "description": "Short pricing descriptor (e.g., 'Free Estimates', 'Varies by depth')."},
        "quickfact_service_area": {"type": "string", "description": "Short description of counties/cities served."}
    }
    
    for i in range(1, num_qa + 1):
        properties[f"qa_{i}_question"] = {"type": "string", "description": f"Question {i} text"}
        properties[f"qa_{i}_answer"] = {"type": "string", "description": f"Answer {i} text. Rule R-118: First sentence must directly and completely answer the question as if spoken out loud, avoiding summary statements or bulleted lists. Subsequent sentences can add detail. Do not use lists."}
        
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys())
    }

def get_prompt(name, city, state, county, website, crawled_text, num_qa, questions):
    """
    Builds the detailed system instruction prompt for Gemini.
    """
    q_list_str = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions[:num_qa])])
    
    # Truncate text to avoid blowing up the token quota
    max_chars = 20000
    if len(crawled_text) > max_chars:
        crawled_text = crawled_text[:max_chars] + "\n...[TRUNCATED FOR LENGTH]..."
        
    prompt = f"""
We are enriching a business listing directory for water well contractors.
Below is the crawled website text and metadata for a contractor.

Metadata:
- Name: {name}
- City: {city}
- State: {state}
- County: {county}
- Website: {website}

Crawled Website Text:
---
{crawled_text}
---

Your task is to analyze the crawled text (supplementing with general geographical and industry context where information is missing) and return a JSON object conforming to the schema.

Important Intent Detection Rules:
1. 24/7 Emergency Pump Repairs (emergency_repair_247): Look for emergency keywords (e.g. "24/7", "emergency pump service", "no water").
2. Water Quality & Treatment (water_testing_offered / water_treatment_installed): Identify specialists checking for "sulfur", "iron", "rotten egg smell", or installing softeners.
3. Pressure Switch & Bladder Tank Services (pressure_tank_services): Look for "pressure switch", "bladder tank", "well tank", or "rapid cycling" to identify diagnostic repair capabilities.
4. Permitting & Heavy Drilling (handles_new_permits): Identify heavy drillers ("air rotary", "well casing", "well rehabilitation") and track if they handle county permitting.

Important Q&A Generation Rules (Rule R-118):
You must generate exactly {num_qa} Q&A blocks answering these questions:
{q_list_str}

For each answer:
- The first sentence of the answer must directly and completely answer the question as if spoken out loud, avoiding summary statements, filler, or bulleted lists.
- Subsequent sentences should add detail.
- Do NOT use bullet points or lists in the answers. Keep them conversational and direct.
"""
    return prompt

def get_pending_records(db_path, state_abbrev):
    """
    Queries database for rows that have website crawled text files available.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    if state_abbrev:
        c.execute("""
            SELECT id, name, slug, website_url, city, state, county
            FROM well_contractors
            WHERE UPPER(state) = ?
              AND (data_freshness IS NULL OR data_freshness != 'enriched')
        """, (state_abbrev,))
    else:
        c.execute("""
            SELECT id, name, slug, website_url, city, state, county
            FROM well_contractors
            WHERE (data_freshness IS NULL OR data_freshness != 'enriched')
        """)
        
    rows = c.fetchall()
    conn.close()
    
    pending = []
    for row in rows:
        row_id, name, slug, website_url, city, state, county = row
        state_folder = STATE_TO_FOLDER.get((state or "").upper(), "general")
        
        # Look for crawled text file
        cache_path = utils.resolve_path(f"02-workbench/03-wells-water-well-drillers/cache/crawled_text/general/{slug}.txt")
        if not os.path.exists(cache_path):
            # Fallback to state folder if it exists
            cache_path = utils.resolve_path(f"02-workbench/03-wells-water-well-drillers/cache/crawled_text/{state_folder}/{slug}.txt")
            
        text = ""
        if os.path.exists(cache_path):
            # Read text
            with open(cache_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
                
            # If it explicitly failed, clear the text
            if text.startswith("Crawl Failed"):
                text = ""
                
        pending.append({
            "id": row_id,
            "name": name,
            "slug": slug,
            "website_url": website_url,
            "city": city,
            "state": state,
            "county": county,
            "crawled_text": text
        })
                
    return pending

def update_database(db_path, record_id, data):
    """
    Updates the sqlite database record with enriched fields.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    set_clause = []
    values = []
    for key, val in data.items():
        set_clause.append(f"{key} = ?")
        values.append(val)
        
    # Audit tracking fields
    set_clause.append("enriched_at = datetime('now')")
    set_clause.append("enrichment_source = ?")
    values.append("gemini-2.5-flash")
    set_clause.append("data_freshness = ?")
    values.append("enriched")
    
    values.append(record_id)
    query = f"UPDATE well_contractors SET {', '.join(set_clause)} WHERE id = ?"
    c.execute(query, values)
    conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Enrich well contractors with Gemini capabilities analysis and Q&A content.")
    parser.add_argument("--state", type=str, default="all", help="State to enrich (e.g. georgia, texas, or 'all').")
    parser.add_argument("--mode", type=str, choices=["validation", "full"], default="validation", help="Validation mode (5 records, 7 Q&As) or full mode (all records, 10 Q&As).")
    parser.add_argument("--limit", type=int, help="Optional record limit (defaults to 5 in validation mode).")
    parser.add_argument("--db", type=str, help="Direct path to SQLite database. Defaults to unified database.")
    
    args = parser.parse_args()
    
    state = args.state
    mode = args.mode
    limit = args.limit
    
    if mode == "validation" and limit is None:
        limit = 5
        
    # Resolve database path
    if args.db:
        db_path = os.path.abspath(args.db)
    else:
        db_path = utils.get_unified_db_path()
        
    if not os.path.exists(db_path):
        print(f"[-] Error: Database not found at: {db_path}")
        sys.exit(1)
        
    # Load API Key
    api_key = load_gemini_api_key()
    if not api_key:
        print("[-] Error: Gemini/Google API Key not found in environment variables or .env file.")
        sys.exit(1)
        
    # Initialize Gemini client wrapper
    call_gemini = init_gemini_client(api_key)
    
    # Resolve state filtering
    state_abbrev = None
    if state and state.lower() != 'all':
        state_map = {
            "georgia": "GA", "michigan": "MI", "new york": "NY", "new_york": "NY",
            "north carolina": "NC", "north_carolina": "NC", "ohio": "OH",
            "pennsylvania": "PA", "texas": "TX", "virginia": "VA",
            "arizona": "AZ",
            "ga": "GA", "mi": "MI", "ny": "NY", "nc": "NC", "oh": "OH",
            "pa": "PA", "tx": "TX", "va": "VA", "az": "AZ"
        }
        state_abbrev = state_map.get(state.lower(), state.upper())
        
    print(f"[*] Target Database Path: {db_path}")
    print(f"[*] Target State Filter: {state_abbrev if state_abbrev else 'All'}")
    print(f"[*] Enrichment Mode: {mode.upper()}")
    print(f"[*] Execution Limit: {limit if limit else 'No Limit'}")
    
    # Query database and find records with crawled text
    pending_records = get_pending_records(db_path, state_abbrev)
    print(f"[*] Found {len(pending_records)} records with cached website text.")
    
    if not pending_records:
        print("[+] No pending records found with crawled text. Exit.")
        return
        
    # Apply safety limit
    if limit:
        pending_records = pending_records[:limit]
        
    num_qa = 7 if mode == "validation" else 10
    response_schema = get_response_schema(num_qa)
    
    print(f"[*] Starting Gemini enrichment batch of {len(pending_records)} records with 5 parallel workers...")
    
    success_count = 0
    
    def process_record(record):
        prompt = get_prompt(
            name=record['name'],
            city=record['city'],
            state=record['state'],
            county=record['county'],
            website=record['website_url'],
            crawled_text=record['crawled_text'],
            num_qa=num_qa,
            questions=CANONICAL_QUESTIONS
        )
        try:
            result_json = call_gemini(prompt, response_schema)
            return record, result_json, None
        except Exception as e:
            return record, None, e

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_record, record): record for record in pending_records}
        
        for idx, future in enumerate(as_completed(futures)):
            record, result_json, error = future.result()
            
            if error is None:
                # Save to database in main thread to avoid SQLite locking issues
                try:
                    update_database(db_path, record['id'], result_json)
                    print(f"  [{idx+1}/{len(pending_records)}] [+] Successfully updated {record['name']} in SQLite.")
                    success_count += 1
                except Exception as db_e:
                    print(f"  [{idx+1}/{len(pending_records)}] [-] Failed to update DB for {record['name']}: {db_e}")
            else:
                print(f"  [{idx+1}/{len(pending_records)}] [-] Failed to enrich {record['name']}: {error}")
            
    print(f"\n[+] Enrichment run completed:")
    print(f"    - Attempted: {len(pending_records)}")
    print(f"    - Succeeded: {success_count}")
    print(f"    - Failed: {len(pending_records) - success_count}")

if __name__ == "__main__":
    main()
