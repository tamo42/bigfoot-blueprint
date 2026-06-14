import sqlite3
import os
import argparse

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "directory.sqlite"))

def strip_html(html_str):
    import re
    return re.sub('<[^<]+?>', '', html_str) if html_str else ""

def word_count(text):
    return len(text.split()) if text else 0

def validate_records(limit=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, first_name, last_name, city, 
               bar_license_number, listing_content, 
               avatar_investor_faq, avatar_defect_faq, 
               avatar_commercial_faq, avatar_buyer_faq
        FROM attorneys 
        WHERE faq_enriched = 1
    ''')
    records = c.fetchall()
    
    if limit:
        records = records[:limit]
        
    print(f"[*] Found {len(records)} AI-enriched records to validate.")
    
    passed_count = 0
    failed_count = 0
    
    for row in records:
        r_id, f_name, l_name, city, bar_license, content, \
        inv_faq, def_faq, com_faq, buy_faq = row
        
        name = f"{f_name} {l_name}"
        fails = []
        
        # 1. Content Length (> 100 words)
        clean_content = strip_html(content)
        wc = word_count(clean_content)
        if wc < 100:
            fails.append(f"Content too short ({wc} words)")
            
        # 2. Bar License
        if not bar_license or bar_license.strip() == "":
            fails.append("Missing bar license number")
            
        # 3. FAQ Density (> 20 words across all FAQs)
        total_faq_wc = sum([
            word_count(inv_faq), word_count(def_faq), 
            word_count(com_faq), word_count(buy_faq)
        ])
        if total_faq_wc < 20:
            fails.append(f"FAQ too short ({total_faq_wc} words)")
            
        # 4. Core Contact
        if not f_name or not l_name or not city:
            fails.append("Missing core contact info (Name/City)")
            
        if fails:
            print(f"  [-] FAILED: {name} | Reasons: {', '.join(fails)}")
            status = 'draft'
            failed_count += 1
        else:
            print(f"  [+] PASSED: {name}")
            status = 'publish'
            passed_count += 1
            
        c.execute("UPDATE attorneys SET post_status = ? WHERE id = ?", (status, r_id))
        
    conn.commit()
    conn.close()
    
    print("\n===============================")
    print("Validation Run Complete")
    print("===============================")
    print(f"Total Evaluated: {len(records)}")
    print(f"Passed (Published): {passed_count}")
    print(f"Failed (Drafted): {failed_count}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    validate_records(args.limit)

if __name__ == "__main__":
    main()
