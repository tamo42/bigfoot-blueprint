import urllib.request
import json
import csv
import os
import time

def fetch_batch(skip, top):
    url = f"https://api.gabar.org/webservices/membersearch?memberGroup=REALP19&state=GA&skip={skip}&top={top}"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    search_payload = {
        "memberGroup": "REALP19",
        "state": "GA"
    }
    
    data = json.dumps(search_payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode('utf-8')
        return json.loads(res_body)

def main():
    print("=========================================================")
    print("Georgia Closing Attorneys - Direct API Ingestion Engine")
    print("=========================================================")
    
    dest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "georgia-closing-attorneys_seed.csv")
    
    # We will fetch in batches of 500 (efficient, low-load, and fast)
    batch_size = 500
    skip = 0
    all_members = []
    
    print("Initiating direct API queries to GABAR database...")
    
    # 1. First fetch to get the total row count
    try:
        first_batch = fetch_batch(skip, batch_size)
        total_rows = first_batch.get('totalRows', 0)
        members = first_batch.get('members', [])
        all_members.extend(members)
        print(f"Detected {total_rows} total active Real Property Law attorneys in Georgia.")
        print(f"Successfully fetched batch 1 (records {skip + 1} to {skip + len(members)})...")
        skip += batch_size
        
        # 2. Iterate in small batches until we have everything
        while len(all_members) < total_rows and len(members) > 0:
            time.sleep(60) # Polite 60-second delay between API calls to prevent IP blocks
            batch = fetch_batch(skip, batch_size)
            members = batch.get('members', [])
            all_members.extend(members)
            print(f"Successfully fetched batch (records {skip + 1} to {skip + len(members)})...")
            skip += batch_size
            
    except Exception as e:
        print("Error fetching directory data:", e)
        return
        
    print(f"\nCompleted fetching GABAR data. Total records collected: {len(all_members)}")
    
    # 3. Format and save to CSV file
    if not all_members:
        print("No records to save.")
        return
        
    # We flatten the nested 'sections' array for CSV serialization
    for m in all_members:
        sec_names = [s.get('sectionName') for s in m.get('sections', []) if s.get('sectionName')]
        m['sections'] = ", ".join(sec_names)
        m['sections_count'] = len(sec_names)
        
        # Ensure we match GABAR csv headers
        # Rename keys to match the standard importer schema
        m['address1'] = m.get('address1', '')
        m['address2'] = m.get('address2', '')
        m['admission_method'] = m.get('addmissionMethod', '')
        m['admit_date'] = m.get('admitDate', '')
        m['bar_number'] = m.get('barNumber', '')
        m['birth_date'] = m.get('birthDate', '')
        m['cell_phone'] = m.get('cellPhone', '')
        m['city'] = m.get('city', '')
        m['company'] = m.get('company', '')
        m['country'] = m.get('country', '')
        m['county'] = m.get('county', '')
        m['email'] = m.get('email', '')
        m['first_name'] = m.get('firstName', '')
        m['gender'] = m.get('gender', '')
        m['id'] = m.get('id', '')
        m['last_name'] = m.get('lastName', '')
        m['law_school'] = m.get('lawSchool', '')
        m['middle_name'] = m.get('middleName', '')
        m['motion_date'] = m.get('motionDate', '')
        m['nickname'] = m.get('nickname', '')
        m['phone'] = m.get('phone', '')
        m['prefix'] = m.get('prefix', '')
        m['purpose'] = m.get('purpose', '')
        m['relia_guide_id'] = m.get('reliaGuideID', '')
        m['state'] = m.get('state', '')
        m['status'] = m.get('status', '')
        m['suffix'] = m.get('suffix', '')
        m['zip'] = m.get('zip', '')

    headers = [
        "address1", "address2", "admission_method", "admit_date", "bar_number", 
        "birth_date", "cell_phone", "city", "company", "country", "county", 
        "email", "first_name", "gender", "id", "last_name", "law_school", 
        "middle_name", "motion_date", "nickname", "phone", "prefix", "purpose", 
        "relia_guide_id", "sections", "sections_count", "state", "status", "suffix", "zip"
    ]
    
    print(f"Writing dataset to CSV at {dest_path}...")
    try:
        with open(dest_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            for m in all_members:
                writer.writerow(m)
        print("Success! Directory seed data written successfully.")
        print(f"File size: {os.path.getsize(dest_path)} bytes.")
    except Exception as e:
        print("Error writing CSV:", e)

if __name__ == "__main__":
    main()
