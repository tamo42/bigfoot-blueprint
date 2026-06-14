import os
import sys
import json
import sqlite3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "directory.sqlite"))
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", "crawled_text"))

def load_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key: return key
    
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='): return line.split('=', 1)[1].strip()
                elif line.startswith('GOOGLE_API_KEY='): return line.split('=', 1)[1].strip()
    return None

def init_gemini_client(api_key):
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        
        def call_gemini(prompt, response_schema):
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
        return call_gemini
    except ImportError:
        try:
            import google.generativeai as genai_legacy
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
            print("[-] Error: google-genai package not installed.")
            sys.exit(1)

def get_response_schema(has_wholesale, has_title):
    properties = {
        "listing_content": {"type": "string", "description": "Detailed 200-400 words HTML description about the company. Use HTML tags (<p>, <strong>, <ul>, <li>). Do not use markdown."},
        "speakable_what_you_find": {"type": "string", "description": "1-2 sentence spoken summary of what services this firm offers."},
        "speakable_listing_details": {"type": "string", "description": "1-2 sentence spoken summary of licensing and contact info."},
        "speakable_quick_facts": {"type": "string", "description": "1-2 sentence spoken summary starting with 'Key facts:'."},
        "quickfact_best_for": {"type": "string", "description": "Short phrase describing what they are best for, starting with 'This is the right place if you need to...'."},
        "quickfact_primary_items": {"type": "string", "description": "Comma-separated list of 3-4 primary practice areas."},
        "quickfact_fee_structure": {"type": "string", "description": "Clear one-line standard fee summary."},
        "quickfact_access": {"type": "string", "description": "Clear one-line accessibility summary (e.g., mobile closings available)."},
        "avatar_buyer_faq": {"type": "string", "description": "Question: 'What do I need to bring to closing day?' Answer this based on cache."}
    }
    
    if has_wholesale:
        properties["avatar_investor_faq"] = {"type": "string", "description": "Question: 'Do you allow simultaneous or double closings for wholesalers?' Answer based on cache."}
    if has_title:
        properties["avatar_defect_faq"] = {"type": "string", "description": "Question: 'How do you handle heir property title clouds or quiet title actions?' Answer based on cache."}
        
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys())
    }

def get_prompt(name, firm, city, cache_text, has_wholesale, has_title):
    prompt = f"""
You are a legal directory data extractor. Your job is to extract verifiable facts from the provided law firm website cache.
You must strictly obey these rules:
1. DO NOT hallucinate. If the text does not explicitly mention a fee, output: 'Please contact the firm directly for fee estimates.'
2. If the text does not mention simultaneous closings or wholesale contracts, output: 'Please contact the firm directly to verify their policies on simultaneous closings.'
3. Do not make legal claims or guarantee outcomes.

Metadata:
- Attorney Name: {name}
- Firm Name: {firm}
- City: {city}
- Flags: wholesale={has_wholesale}, title_resolution={has_title}

Website Cache:
---
{cache_text}
---

Return a strictly formatted JSON object matching the requested schema.
"""
    return prompt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Optional record limit.")
    args = parser.parse_args()

    api_key = load_gemini_api_key()
    if not api_key:
        print("[-] API Key missing.")
        return
    call_gemini = init_gemini_client(api_key)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, first_name, last_name, firm_name, city, 
               specialty_wholesale, specialty_title_resolution
        FROM attorneys 
        WHERE specialties_crawled = 1 AND (faq_enriched = 0 OR faq_enriched IS NULL)
    ''')
    records = c.fetchall()
    
    if args.limit:
        records = records[:args.limit]
        
    print(f"[*] Found {len(records)} records ready for AI enrichment.")
    
    for row in records:
        r_id, f_name, l_name, firm, city, w_sale, t_res = row
        name = f"{f_name} {l_name}"
        
        cache_path = os.path.join(CACHE_DIR, f"{r_id}.txt")
        if not os.path.exists(cache_path):
            print(f"[-] Missing cache for {name} (ID: {r_id})")
            continue
            
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_text = f.read()
            
        schema = get_response_schema(bool(w_sale), bool(t_res))
        prompt = get_prompt(name, firm, city, cache_text, bool(w_sale), bool(t_res))
        
        print(f"[*] Enriching {name}...")
        try:
            result = call_gemini(prompt, schema)
            
            updates = []
            values = []
            for k, v in result.items():
                updates.append(f"{k} = ?")
                values.append(v)
            
            updates.append("faq_enriched = 1")
            values.append(r_id)
            
            query = f"UPDATE attorneys SET {', '.join(updates)} WHERE id = ?"
            c.execute(query, values)
            conn.commit()
            print(f"  [+] Saved {name}")
            
        except Exception as e:
            print(f"  [-] Failed on {name}: {e}")
            
    conn.close()

if __name__ == "__main__":
    main()
