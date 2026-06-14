import fitz  # PyMuPDF
import sqlite3
import re
import difflib
import os

def clean_name(name):
    # Normalize names for fuzzy matching
    n = name.lower()
    n = re.sub(r'[^a-z0-9\s]', '', n)
    # remove common suffixes
    for suffix in ['llc', 'inc', 'co', 'corp', 'pc', 'services', 'service', 'plumbing', 'septic', 'sanitation', 'pumping', 'pros', 'repair']:
        n = re.sub(r'\b' + suffix + r'\b', '', n)
    return ' '.join(n.split())

def search_pdf(pdf_path, term):
    if not os.path.exists(pdf_path):
        return []
    doc = fitz.open(pdf_path)
    matches = []
    term_clean = clean_name(term)
    
    for i, page in enumerate(doc):
        text = page.get_text("text")
        lines = text.split('\n')
        for line in lines:
            line_clean = clean_name(line)
            if term_clean in line_clean or line_clean in term_clean:
                matches.append((i+1, line))
            elif len(term_clean) > 4 and term_clean[:5] in line_clean:
                matches.append((i+1, line))
    return matches

def main():
    print("Macon Grease & Septic - PDF Roster Parsing")
    print("=========================================")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    
    # Path to site database in user's git workspace
    db_path = r"C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM installers_haulers")
    haulers = cursor.fetchall()
    
    # 1. Print info about the PDFs
    for name, filename in [("MWA Haulers", "mwa_haulers.pdf"), ("DPH Pumpers", "pumpers.pdf"), ("DPH Installers", "installers.pdf")]:
        path = os.path.join(data_dir, filename)
        try:
            doc = fitz.open(path)
            print(f"{name} ({filename}): {len(doc)} pages")
        except Exception as e:
            print(f"Error opening {path}: {e}")
            
    # Search for matching records
    for hid, hname in haulers:
        print(f"\nSearch for: {hname}")
        
        mwa_path = os.path.join(data_dir, "mwa_haulers.pdf")
        mwa_matches = search_pdf(mwa_path, hname)
        if mwa_matches:
            print("  MWA matches:")
            for p, l in mwa_matches[:5]:
                print(f"    Page {p}: {l.strip()}")
                
        pumper_path = os.path.join(data_dir, "pumpers.pdf")
        p_matches = search_pdf(pumper_path, hname)
        if p_matches:
            print("  DPH Pumper matches:")
            for p, l in p_matches[:5]:
                print(f"    Page {p}: {l.strip()}")
                
        installer_path = os.path.join(data_dir, "installers.pdf")
        i_matches = search_pdf(installer_path, hname)
        if i_matches:
            print("  DPH Installer matches:")
            for p, l in i_matches[:5]:
                print(f"    Page {p}: {l.strip()}")

if __name__ == "__main__":
    main()
