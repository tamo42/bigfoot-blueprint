import fitz
import os
import re
import json

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    pdf_path = os.path.join(data_dir, "2026-approved-commercial-haulers-data-base.pdf")
    
    doc = fitz.open(pdf_path)
    records = []
    
    for page_idx in range(len(doc)):
        text = doc[page_idx].get_text("text")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        for idx, line in enumerate(lines):
            if re.match(r'^FOG\d+-\d+$', line):
                fog_id = line
                if idx >= 5:
                    company = lines[idx - 5]
                    city = lines[idx - 4]
                    state = lines[idx - 3]
                    zip_code = lines[idx - 2]
                    phone_tag = lines[idx - 1]
                    
                    records.append({
                        "company": company,
                        "city": city,
                        "state": state,
                        "zip": zip_code,
                        "phone_tag": phone_tag,
                        "fog_id": fog_id,
                        "page": page_idx + 1
                    })
                    
    # Print all unique companies and their FOG IDs
    print(f"Total records found: {len(records)}")
    unique_companies = {}
    for r in records:
        c_name = r["company"]
        if c_name not in unique_companies:
            unique_companies[c_name] = []
        unique_companies[c_name].append(r["fog_id"])
        
    print("\n--- Unique Companies and FOG IDs ---")
    for name, ids in sorted(unique_companies.items()):
        print(f"{name}: {', '.join(ids)}")
        
    # Write to a JSON file
    out_path = os.path.join(data_dir, "extracted_fog_ids.json")
    with open(out_path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"\nSaved extracted records to {out_path}")

if __name__ == "__main__":
    main()
