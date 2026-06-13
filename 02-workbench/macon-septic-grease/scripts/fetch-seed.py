import os
import csv
import json
import requests
from pathlib import Path

# Load dotenv manually to support workspace-level .env files
def load_dotenv():
    # Look for .env in the root directory of the workspace
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

PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

def search_places(query):
    if not PLACES_API_KEY:
        print("Error: GOOGLE_PLACES_API_KEY not found in environment variables or .env file.")
        return []
        
    print(f"Executing Google Places Text Search for: '{query}'...")
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": PLACES_API_KEY
    }
    
    results = []
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results.extend(data.get("results", []))
        
        # Handle pagination if more than 20 results exist
        next_page_token = data.get("next_page_token")
        while next_page_token:
            import time
            time.sleep(2) # Google requires a short delay before the next_page_token becomes active
            print("Fetching next page of results...")
            paginated_params = {
                "pagetoken": next_page_token,
                "key": PLACES_API_KEY
            }
            res = requests.get(url, params=paginated_params, timeout=30)
            res.raise_for_status()
            pdata = res.json()
            results.extend(pdata.get("results", []))
            next_page_token = pdata.get("next_page_token")
            
    except Exception as e:
        print(f"Error during search: {e}")
        
    return results

def main():
    queries = [
        "septic pumping Macon GA",
        "grease trap cleaning Macon GA",
        "septic tank installers Bibb County GA"
    ]
    
    all_places = {}
    for q in queries:
        places = search_places(q)
        print(f"  Found {len(places)} results.")
        for p in places:
            place_id = p.get("place_id")
            if place_id and place_id not in all_places:
                all_places[place_id] = p
                
    print(f"\nTotal unique businesses found: {len(all_places)}")
    
    # Ensure data directory exists
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = data_dir / "septic-grease-seed.csv"
    
    # Headers matching SQLite schema targets
    headers = [
        "name", "place_id", "address", "city", "state", "zip_code", 
        "latitude", "longitude", "google_rating", "google_review_count"
    ]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for p in all_places.values():
            # Parse formatted_address to separate city/state/zip if possible
            formatted_address = p.get("formatted_address", "")
            
            # Simple address parsing logic: Address format is usually: "Street, City, ST ZIP, Country"
            # E.g. "123 Cherry St, Macon, GA 31201, USA"
            address_parts = [part.strip() for part in formatted_address.split(",")]
            
            street_address = address_parts[0] if len(address_parts) > 0 else ""
            city = "Macon"
            state = "GA"
            zip_code = ""
            
            # Look for zip code in parts
            for part in address_parts:
                if "GA " in part:
                    zip_part = part.replace("GA ", "").strip()
                    if zip_part.isdigit() and len(zip_part) == 5:
                        zip_code = zip_part
                        break
                        
            # Get geometry
            loc = p.get("geometry", {}).get("location", {})
            
            writer.writerow({
                "name": p.get("name"),
                "place_id": p.get("place_id"),
                "address": formatted_address, # Save full formatted address as default
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "latitude": loc.get("lat"),
                "longitude": loc.get("lng"),
                "google_rating": p.get("rating", 0.0),
                "google_review_count": p.get("user_ratings_total", 0)
            })
            
    print(f"Successfully generated seed CSV: {csv_file.name}")

if __name__ == "__main__":
    main()
