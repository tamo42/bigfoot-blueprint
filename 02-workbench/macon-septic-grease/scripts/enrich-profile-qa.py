import os
import sys
import json
import sqlite3
import argparse
import time
import requests
from pathlib import Path

# Load dotenv manually to support workspace-level .env files
def load_dotenv():
    root_dir = Path(__file__).resolve().parents[3]
    env_path = root_dir / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

load_dotenv()

# We will check both GEMINI_API_KEY and general GOOGLE_PLACES_API_KEY (in case it is unrestricted)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Fallback to the places key if it is general and enables Generative Language API
    GEMINI_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

def generate_profile_aeo(business_data):
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY or GOOGLE_PLACES_API_KEY not found in environment.")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Format specialty lists
    specialties = []
    if business_data.get("specialty_grease_trap"): specialties.append("Commercial Grease Trap Pumping & Interceptor Cleaning")
    if business_data.get("specialty_septic_pump"): specialties.append("Residential & Commercial Septic Tank Pumping")
    if business_data.get("specialty_riser_install"): specialties.append("Septic Riser and Lid Installation")
    if business_data.get("specialty_line_jetting"): specialties.append("High-Pressure Hydro Jetting / Sewer Line Jetting")
    if business_data.get("specialty_inspections"): specialties.append("Real Estate Septic Inspections & Dye Testing")
    if business_data.get("specialty_emergency_dispatch"): specialties.append("24/7 Emergency Dispatch / Backup Pumping")
    
    specialties_str = ", ".join(specialties) if specialties else "General Septic Pumping & Liquid Waste Hauling"
    
    reviews = json.loads(business_data.get("reviews_json", "[]"))
    reviews_str = "\n".join([f"- {r}" for r in reviews]) if reviews else "No Google reviews available."

    prompt_text = f"""
You are an expert SEO and Answer Engine Optimization (AEO) copywriter specializing in home services and commercial utility directories.
Your task is to write high-quality, localized marketing copy and a compliance Q&A guide for a septic and grease hauling provider in Macon, Georgia.

Business Details:
- Name: {business_data['name']}
- Address: {business_data['address']}
- City: {business_data['city']}
- State: {business_data['state']}
- Phone: {business_data['phone']}
- Website: {business_data['website_url']}
- Rating: {business_data['google_rating']} ({business_data['google_review_count']} reviews)
- Identified Service Specialties: {specialties_str}
- Customer Reviews:
{reviews_str}

Regulatory Background Context (Include or reference in copy and Q&A as appropriate):
1. Macon Water Authority (MWA) Grease Regulations:
   - Inspections: MWA performs grease trap/interceptor inspections of commercial food service establishments on a quarterly basis.
   - The 25% Pumping Rule: Interceptors must be pumped when the combined thickness of the Fats, Oils, and Grease (FOG) layer and Food Solids layer reaches 25% of the total liquid capacity, or quarterly, whichever occurs first.
   - FOG Limit: Wastewater discharge exceeding 300 mg/L is strictly prohibited under MWA code.
   - Manifests: Establishments must submit and retain waste manifests from approved, permitted grease haulers.
2. Georgia Department of Public Health (DPH) Septic Regulations:
   - Licensing: Septic installation and septage hauling must be conducted by a state DPH-certified contractor.
   - Local Permit: Haulers must hold an active County Septage Removal Permit from the local health department.

Writing Requirements:
1. 'profile_bio':
   - Write a 200-to-300-word business summary.
   - Focus on the services they offer, their local reputation, and how they serve Macon and Bibb County.
   - Do NOT use hedging or tentative language (e.g., do not say 'according to their website', 'they claim to', or 'reportedly'). State their offerings as objective, definitive facts (e.g., '{business_data['name']} provides...').
   - Keep it engaging, professional, and SEO-dense.
2. 'speakable_bio':
   - Write a 2-3 sentence (40-60 words) summary.
   - Tailor it to be suitable for screen readers or search snippets (speakable markup).
3. 'faq':
   - Generate exactly 20 Q&As in a list.
   - Integrate the specific local regulations (MWA 25% rule, 300 mg/L discharge limits, quarterly pumping, state DPH certs, County Septage Permits, manifest reporting) and relate them to this business's services.
   - Questions should be natural and range from service-specific questions to local compliance questions. Format answers to be concise, helpful, and authoritative.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_text
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "profile_bio": {
                        "type": "STRING",
                        "description": "A 200-to-300-word business summary focusing on the services they offer in Macon, GA. Do not use hedging or tentative language."
                    },
                    "speakable_bio": {
                        "type": "STRING",
                        "description": "Short speakable bio, target block text for CSS selector, summarizing what the business is and services in 2-3 sentences."
                    },
                    "faq": {
                        "type": "ARRAY",
                        "description": "An array of exactly 20 local regulatory and service-related Q&As for the specific business profile.",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "question": {
                                    "type": "STRING"
                                },
                                "answer": {
                                    "type": "STRING"
                                }
                            },
                            "required": ["question", "answer"]
                        }
                    }
                },
                "required": ["profile_bio", "speakable_bio", "faq"]
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        
        # Handle key errors or quota blocks
        if response.status_code == 403:
            print(f"API Error 403: Access is blocked. Verify that GEMINI_API_KEY is correct and enables the Generative Language API.")
            print(response.text)
            return None
        elif response.status_code != 200:
            print(f"Gemini API returned error code {response.status_code}:")
            print(response.text)
            return None
            
        res_json = response.json()
        candidates = res_json.get("candidates", [])
        if not candidates:
            print("Error: No candidates returned in Gemini response.")
            return None
            
        content_text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
        # Parse the inner JSON
        return json.loads(content_text)
        
    except Exception as e:
        print(f"Exception calling Gemini API: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Enrich database with Gemini-generated profile bio and Q&As.")
    parser.add_argument("--limit", type=int, default=5, help="Limit the number of records to process (default: 5)")
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    db_file = script_dir.parent / "data" / "directory.sqlite"
    
    if not db_file.exists():
        print(f"Error: Database file '{db_file.name}' not found. Run import-seed.py first.")
        return
        
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Query records where profile_bio is NULL or faq_json is empty array
    c.execute("""
        SELECT * 
        FROM installers_haulers 
        WHERE profile_bio IS NULL OR faq_json = '[]' OR speakable_bio IS NULL
        LIMIT ?
    """, (args.limit,))
    
    records = c.fetchall()
    
    if not records:
        print("No pending unenriched records found in database.")
        conn.close()
        return
        
    print(f"Enriching {len(records)} records using Gemini API (Limit: {args.limit})...")
    
    success_count = 0
    for i, row in enumerate(records):
        record_id = row["id"]
        name = row["name"]
        
        print(f"\n[{i+1}/{len(records)}] Requesting AI copywriting for: '{name}' (ID: {record_id})...")
        
        # Call Gemini API
        enriched = generate_profile_aeo(dict(row))
        
        if enriched:
            profile_bio = enriched.get("profile_bio")
            speakable_bio = enriched.get("speakable_bio")
            faq_list = enriched.get("faq", [])
            faq_json = json.dumps(faq_list)
            
            # Print a quick preview
            print(f"  [+] Generated Bio ({len(profile_bio.split())} words)")
            print(f"  [+] Speakable Bio: '{speakable_bio}'")
            print(f"  [+] Generated {len(faq_list)} FAQs")
            
            # Update database
            c.execute("""
                UPDATE installers_haulers
                SET profile_bio = ?,
                    speakable_bio = ?,
                    faq_json = ?
                WHERE id = ?
            """, (profile_bio, speakable_bio, faq_json, record_id))
            
            conn.commit()
            success_count += 1
            print(f"  [+] Committed ID {record_id} updates to database.")
        else:
            print(f"  [-] Failed to generate content for: '{name}'. Stopping batch to prevent errors.")
            break
            
        # Add politeness delay
        time.sleep(1.0)
        
    conn.close()
    print(f"\nAI Enrichment Batch Complete. Successfully processed {success_count} records.")

if __name__ == "__main__":
    main()
