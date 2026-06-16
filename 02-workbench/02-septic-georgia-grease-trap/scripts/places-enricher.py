import sqlite3
import requests
import json
import time
import os
import re

# Load .env manually since dotenv might not be installed
env_path = r'C:\Users\tamo4\git\nhq-bigfoot-blueprint\.env'
api_key = None
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('GOOGLE_PLACES_API_KEY='):
                api_key = line.split('=', 1)[1].strip()

if not api_key:
    print("No Google Places API key found in .env")
    exit(1)

db_path = r'C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get haulers missing website or lat/long
c.execute("SELECT id, name, city, fleet_size FROM installers_haulers WHERE website_url IS NULL OR manual_lat IS NULL")
rows = c.fetchall()

print(f"Found {len(rows)} haulers to enrich.")

updated_count = 0

for row in rows:
    h_id, name, city, fleet_size = row
    city = city if city else "Georgia"
    
    # Clean name for search
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    search_query = f"{clean_name} {city} Georgia"
    
    print(f"\nSearching for: {search_query}")
    
    # 1. Find Place
    find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    find_params = {
        'input': search_query,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': api_key
    }
    
    try:
        find_res = requests.get(find_url, params=find_params).json()
        
        website = None
        lat = None
        lng = None
        rating = None
        reviews_count = None
        r1_text = r1_auth = r1_rating = None
        r2_text = r2_auth = r2_rating = None
        r3_text = r3_auth = r3_rating = None
        
        if find_res.get('status') == 'OK' and len(find_res.get('candidates', [])) > 0:
            place_id = find_res['candidates'][0]['place_id']
            
            # 2. Place Details
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'fields': 'website,geometry,rating,user_ratings_total,reviews',
                'key': api_key
            }
            
            det_res = requests.get(details_url, params=details_params).json()
            if det_res.get('status') == 'OK':
                result = det_res.get('result', {})
                website = result.get('website')
                if result.get('geometry') and result['geometry'].get('location'):
                    lat = result['geometry']['location'].get('lat')
                    lng = result['geometry']['location'].get('lng')
                
                rating = result.get('rating')
                reviews_count = result.get('user_ratings_total')
                
                reviews = result.get('reviews', [])
                if len(reviews) > 0:
                    r1_text = reviews[0].get('text')
                    r1_auth = reviews[0].get('author_name')
                    r1_rating = reviews[0].get('rating')
                if len(reviews) > 1:
                    r2_text = reviews[1].get('text')
                    r2_auth = reviews[1].get('author_name')
                    r2_rating = reviews[1].get('rating')
                if len(reviews) > 2:
                    r3_text = reviews[2].get('text')
                    r3_auth = reviews[2].get('author_name')
                    r3_rating = reviews[2].get('rating')
        else:
            print("  -> No place found.")
            
        # 3. Expanded FAQs (qa_3, qa_4, qa_5)
        qa_3_q = "How often is my commercial kitchen required to pump its grease trap?"
        qa_3_a = f"Under the standard Georgia 25% Rule, {name} recommends pumping when combined fats, oils, grease, and settled solids reach 25% of the total liquid depth, or at least quarterly."
        
        qa_4_q = "What documentation do I need for municipal FOG audits?"
        qa_4_a = f"When {name} services your interceptor, they will provide a physical pumping manifest. You are required by most local authorities to maintain these records on-site for a minimum of 3 years."
        
        qa_5_q = "Does this company handle interceptor blockages and backups?"
        qa_5_a = f"Yes, alongside routine liquid waste hauling, active commercial pumpers are equipped to handle urgent line jetting and localized backups for their commercial accounts."

        # Update DB
        update_query = """
            UPDATE installers_haulers 
            SET website_url = ?, manual_lat = ?, manual_lng = ?, 
                google_rating = ?, google_review_count = ?,
                review_1_text = ?, review_1_author = ?, review_1_rating = ?,
                review_2_text = ?, review_2_author = ?, review_2_rating = ?,
                review_3_text = ?, review_3_author = ?, review_3_rating = ?,
                qa_3_question = ?, qa_3_answer = ?,
                qa_4_question = ?, qa_4_answer = ?,
                qa_5_question = ?, qa_5_answer = ?
            WHERE id = ?
        """
        
        c.execute(update_query, (
            website, lat, lng, rating, reviews_count,
            r1_text, r1_auth, r1_rating,
            r2_text, r2_auth, r2_rating,
            r3_text, r3_auth, r3_rating,
            qa_3_q, qa_3_a, qa_4_q, qa_4_a, qa_5_q, qa_5_a,
            h_id
        ))
        
        updated_count += 1
        
        # Sleep to respect API rate limits
        time.sleep(0.5)

    except Exception as e:
        print(f"Error enriching {name}: {e}")

conn.commit()
conn.close()
print(f"\nSuccessfully enriched {updated_count} providers!")
