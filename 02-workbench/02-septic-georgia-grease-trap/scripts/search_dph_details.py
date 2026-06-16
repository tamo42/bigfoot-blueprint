import fitz
import re

db_phones = {
    1: "4784294144", # Underground Septic
    2: "4787462004", # A-1 Sanitation
    3: "4783306475", # Fast Flow
    4: "4784742653", # Stewart
    5: "4782027130", # Septic Tank Pros
    6: "7065908426", # Big Daddy
    7: "4782730033", # ASAP Septic (WR)
    8: "4787427423", # Kitchens & Young
    9: "7704837802", # Bowen's
    10: "4783082811", # ASAP Septic (Macon)
    11: "4045520079", # A1 Pumping
    12: "4789529114", # ASAP Septic (Perry)
    13: "4783126655", # Ricky Heath
    14: "4046275931", # Environmental Remedies
    15: "4787889398", # Safety-Kleen
    16: "4785953906", # AmeriPro
    17: "4782076681", # Mr. Rooter
    18: "4782501391", # SERVPRO
    19: "4787889274", # Extreme Clean
    20: "4789575674", # JTL Sitework
}

db_names = {
    1: "Underground Septic",
    2: "A-1 Sanitation",
    3: "Fast Flow",
    4: "Stewart Septic",
    5: "Septic Tank Pros",
    6: "Big Daddy",
    7: "ASAP Septic",
    8: "Kitchens & Young",
    9: "Bowen",
    10: "ASAP Septic",
    11: "A1 Pumping",
    12: "ASAP Septic",
    13: "Ricky Heath",
    14: "Environmental Remedies",
    15: "Safety-Kleen",
    16: "AmeriPro",
    17: "Mr. Rooter",
    18: "SERVPRO",
    19: "Extreme Clean",
    20: "JTL Sitework",
}

def clean_phone(p):
    return re.sub(r'\D', '', p)

def search_pdf(path, pdf_name):
    print(f"\n=== Searching {pdf_name} ({path}) ===")
    doc = fitz.open(path)
    # Extract text with page breaks
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text("text"))
        
    for db_id, name in db_names.items():
        phone = db_phones[db_id]
        phone_suffix = phone[-4:]
        found = False
        
        # Search by phone suffix first
        for p_idx, text in enumerate(pages_text):
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for l_idx, line in enumerate(lines):
                if phone_suffix in clean_phone(line) or clean_phone(phone) in clean_phone(line):
                    print(f"  ID {db_id} ({name}): Found phone match on page {p_idx+1}: '{line}'")
                    # print surrounding lines
                    start = max(0, l_idx - 2)
                    end = min(len(lines), l_idx + 3)
                    print("    Context:")
                    for idx in range(start, end):
                        marker = "--> " if idx == l_idx else "    "
                        print(f"{marker}{lines[idx]}")
                    found = True
                    
        # If not found by phone, search by name substring
        if not found:
            for p_idx, text in enumerate(pages_text):
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                for l_idx, line in enumerate(lines):
                    if name.lower() in line.lower():
                        print(f"  ID {db_id} ({name}): Found name match on page {p_idx+1}: '{line}'")
                        start = max(0, l_idx - 2)
                        end = min(len(lines), l_idx + 3)
                        print("    Context:")
                        for idx in range(start, end):
                            marker = "--> " if idx == l_idx else "    "
                            print(f"{marker}{lines[idx]}")
                        found = True

search_pdf(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\pumpers.pdf", "DPH Pumpers")
search_pdf(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\02-septic-georgia-grease-trap\data\installers.pdf", "DPH Installers")
