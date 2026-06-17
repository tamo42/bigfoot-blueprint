import os
import json
import sqlite3
import argparse
import concurrent.futures
import threading
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Locks
log_lock = threading.Lock()
rate_limit_lock = threading.Lock()
last_request_time = 0.0

def process_single_contractor(client, cid, name, reviews_json, dimensions, dim_keys):
    """Worker function to process a single contractor's reviews via Gemini."""
    try:
        reviews_list = json.loads(reviews_json)
        texts = []
        for r in reviews_list:
            if isinstance(r, dict) and r.get('text'):
                texts.append(r['text'])
            elif isinstance(r, str):
                texts.append(r)
                
        if not texts:
            return cid, name, "{}", "No text in reviews"
            
        reviews_text_block = "\n---\n".join(texts)
    except Exception as e:
        return cid, name, None, f"Failed to parse reviews: {e}"

    prompt = f"""
You are an objective business analyst. Analyze the following Google Reviews for the business "{name}".
Abstract the reviews into a structured scorecard and text summary.

SCORE DIMENSIONS (1 to 10 scale):
1. {dimensions[0]}
2. {dimensions[1]}
3. {dimensions[2]}
4. {dimensions[3]}

Based on the reviews, estimate a score for each dimension. If the reviews don't mention a dimension, estimate a neutral score (e.g., 5 or 6).
Also calculate an `overall_score` (1.0 to 10.0, can be a decimal).

Return ONLY valid JSON in the exact following format, with NO markdown formatting around it:
{{
  "scores": {{
    "{dim_keys[0]}": 8,
    "{dim_keys[1]}": 7,
    "{dim_keys[2]}": 9,
    "{dim_keys[3]}": 8,
    "overall_score": 8.0
  }},
  "summary": "A 2-3 sentence synthesizer of the key themes...",
  "positive_points": ["bullet 1", "bullet 2"],
  "neutral_points": ["bullet 1"],
  "negative_points": ["bullet 1"]
}}

REVIEWS:
{reviews_text_block}
"""
    
    try:
        global last_request_time
        with rate_limit_lock:
            now = time.time()
            elapsed = now - last_request_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            last_request_time = time.time()
            
        # Network call is OUTSIDE the lock to allow concurrency!
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'temperature': 0.1}
        )
        
        raw_text = response.text
        
        # Thread-safe logging of raw response
        with log_lock:
            with open('gemini_responses.log', 'a', encoding='utf-8') as f:
                f.write(f"\n[{cid}] {name} RAW RESPONSE:\n{raw_text}\n{'='*50}\n")
        
        raw_json = raw_text.strip()
        if raw_json.startswith('```json'):
            raw_json = raw_json[7:-3]
        elif raw_json.startswith('```'):
            raw_json = raw_json[3:-3]
            
        parsed = json.loads(raw_json.strip())
        return cid, name, json.dumps(parsed), None
        
    except Exception as e:
        err_msg = str(e)
        if 'response' in locals() and hasattr(response, 'text'):
            err_msg += f"\nResponse: {response.text}"
        return cid, name, None, f"Gemini API/Parse Error: {err_msg}"

def run_enrichment(db_path, dimensions, limit=None, state=None):
    client = genai.Client()
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    query = """
        SELECT id, name, reviews_json 
        FROM well_contractors 
        WHERE reviews_json IS NOT NULL AND reviews_json != '[]' AND reviews_json != ''
        AND review_analysis_json IS NULL
    """
    if state:
        query += f" AND state = '{state}'"
    if limit:
        query += f" LIMIT {limit}"
        
    c.execute(query)
    rows = c.fetchall()
    
    dim_names = ", ".join(dimensions)
    print(f"[*] Found {len(rows)} contractors to enrich for dimensions: {dim_names}", flush=True)
    
    dim_keys = [d.lower().replace(' ', '_') for d in dimensions]
    
    # Process concurrently using ThreadPoolExecutor
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all tasks
        future_to_cid = {
            executor.submit(process_single_contractor, client, row[0], row[1], row[2], dimensions, dim_keys): row[0]
            for row in rows
        }
        
        # Process as they complete
        for future in concurrent.futures.as_completed(future_to_cid):
            cid, name, result_json, err = future.result()
            
            if err:
                print(f"[-] Failed ID {cid} ({name}): {err}", flush=True)
                if result_json == "{}":
                    # It was a graceful empty skip
                    c.execute("UPDATE well_contractors SET review_analysis_json = ? WHERE id = ?", ("{}", cid))
                    conn.commit()
            elif result_json:
                try:
                    c.execute("UPDATE well_contractors SET review_analysis_json = ? WHERE id = ?", (result_json, cid))
                    conn.commit()
                    
                    parsed = json.loads(result_json)
                    score = parsed.get('scores', {}).get('overall_score', 'N/A')
                    print(f"[+] Saved ID {cid} ({name}): {score}/10", flush=True)
                    success_count += 1
                except sqlite3.Error as db_err:
                    print(f"[-] DB Error saving ID {cid} ({name}): {db_err}", flush=True)
            
    conn.close()
    print(f"\n[*] Enrichment complete. Successfully saved {success_count} records.", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=r"C:\Users\tamo4\git\bigfoot-sites\uswelldrillers.com\src\data\water_well_directory.sqlite")
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--dim1', default="Customer Service")
    parser.add_argument('--dim2', default="Speed")
    parser.add_argument('--dim3', default="Cost")
    parser.add_argument('--dim4', default="Work Quality")
    parser.add_argument('--state', default=None)
    args = parser.parse_args()
    
    run_enrichment(args.db, [args.dim1, args.dim2, args.dim3, args.dim4], args.limit, args.state)
