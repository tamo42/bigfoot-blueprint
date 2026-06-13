import fitz  # PyMuPDF
import os
import re

def print_pdf_matches(pdf_path, name):
    if not os.path.exists(pdf_path):
        return
    doc = fitz.open(pdf_path)
    clean_n = name.lower().replace(",", "").replace(".", "").replace(" llc", "").replace(" inc", "").strip()
    # take first word or two for search
    words = clean_n.split()
    if not words:
        return
    search_term = words[0]
    if len(words) > 1 and len(words[0]) <= 3: # if first word is short (e.g. A-1 or JTL), search for first two words
        search_term = f"{words[0]} {words[1]}"
        
    print(f"\n--- Searching {os.path.basename(pdf_path)} for '{search_term}' (from '{name}') ---")
    
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        lines = text.split('\n')
        for idx, line in enumerate(lines):
            if search_term.lower() in line.lower():
                # print 4 lines before and 6 lines after to capture formatting
                start = max(0, idx - 4)
                end = min(len(lines), idx + 7)
                print(f"Match on Page {page_num + 1}:")
                for i in range(start, end):
                    marker = ">>> " if i == idx else "    "
                    print(f"{marker}{lines[i].strip()}")
                print("-" * 40)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    
    # 20 companies in Macon-Bibb
    companies = [
        "Underground Septic Services",
        "A-1 Sanitation",
        "Fast Flow Septic",
        "Stewart Septic",
        "Septic Tank Pros",
        "Big Daddy's Septic",
        "ASAP Septic",
        "Kitchens & Young",
        "Bowen",
        "A1 Pumping",
        "Ricky Heath",
        "Environmental Remedies",
        "Safety-Kleen",
        "AmeriPro",
        "Mr. Rooter",
        "Servpro",
        "Extreme Clean",
        "JTL Sitework"
    ]
    
    mwa_path = os.path.join(data_dir, "mwa_haulers.pdf")
    pump_path = os.path.join(data_dir, "pumpers.pdf")
    inst_path = os.path.join(data_dir, "installers.pdf")
    
    for company in companies:
        print(f"\n==========================================")
        print(f"DETAILS FOR: {company}")
        print(f"==========================================")
        print_pdf_matches(mwa_path, company)
        print_pdf_matches(pump_path, company)
        print_pdf_matches(inst_path, company)

if __name__ == "__main__":
    main()
