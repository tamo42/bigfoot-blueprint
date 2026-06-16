import urllib.request
import urllib.parse
import json
import time
import os
import sys

def get_project_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(current, ".env")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            # Fallback to current script directory's grandparent if no .env found
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        current = parent

def load_apify_token():
    root = get_project_root()
    env_path = os.path.join(root, ".env")
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                if key.strip() == "APIFY_API_TOKEN":
                    return val.strip().strip('"').strip("'")
    return None

def main():
    print("=========================================================")
    print("Georgia Closing Attorneys - Automated Apify Seed Fetcher")
    print("=========================================================")
    
    token = load_apify_token()
    if not token:
        print("Error: APIFY_API_TOKEN not found in .env file. Exiting.")
        sys.exit(1)


    # Input parameters for GABAR scraper
    # states: ["GA"] specifies Georgia members
    # max_items: 50 runs a quick, low-cost iteration to verify schema & data structure
    # max_concurrency: 2 is sufficient for a small run
    actor_input = {
        "states": ["GA"],
        "max_items": 50,
        "max_concurrency": 2
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    actor_id = "captivating_clarinet/gabar-member-directory-scraper"
    start_url = f"https://api.apify.com/v2/acts/{actor_id.replace('/', '~')}/runs?token={token}"
    
    print(f"Triggering Apify Actor '{actor_id}' for Georgia (GA) members (limit: 50)...")
    
    data = json.dumps(actor_input).encode('utf-8')
    req = urllib.request.Request(start_url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            run_data = json.loads(res_body)
            run_id = run_data['data']['id']
            dataset_id = run_data['data']['defaultDatasetId']
            print(f"Actor started successfully! Run ID: {run_id}")
    except Exception as e:
        print(f"Error starting actor: {e}")
        sys.exit(1)
        
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"
    print("Polling actor run status (checking every 5 seconds)...")
    
    while True:
        try:
            req_status = urllib.request.Request(status_url, method='GET')
            with urllib.request.urlopen(req_status) as response:
                res_body = response.read().decode('utf-8')
                run_status_data = json.loads(res_body)
                status = run_status_data['data']['status']
                
                print(f"Current Status: {status}")
                if status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
                    if status == 'SUCCEEDED':
                        print("\nScraping complete and successful!")
                        break
                    else:
                        print(f"\nScraping failed with status: {status}")
                        sys.exit(1)
        except Exception as e:
            print(f"Error checking status: {e}")
            
        time.sleep(5)
        
    # Download the dataset in CSV format
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}&format=csv&clean=true"
    dest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "01-gabar-georgia-closing-attorneys_seed.csv")
    
    print(f"Downloading dataset as CSV and saving to {dest_path}...")
    
    try:
        urllib.request.urlretrieve(dataset_url, dest_path)
        print("Success! Seed data downloaded and saved successfully.")
        print(f"File size: {os.path.getsize(dest_path)} bytes.")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
