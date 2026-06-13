import fitz  # PyMuPDF
import sqlite3
import re
import difflib

def clean_name(name):
    # Normalize names for fuzzy matching
    n = name.lower()
    n = re.sub(r'[^a-z0-9\s]', '', n)
    # remove common suffixes
    for suffix in ['llc', 'inc', 'co', 'corp', 'pc', 'services', 'service', 'plumbing', 'septic', 'sanitation', 'pumping']:
        n = re.sub(r'\b' + suffix + r'\b', '', n)
    return ' '.join(n.split())

def search_pdf(pdf_path, term):
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
            elif difflib.SequenceMatcher(None, term_clean, line_clean).ratio() > 0.6:
                matches.append((i+1, line))
    return matches

def main():
    print("Macon Grease & Septic - PDF Roster Parsing")
    print("=========================================")
    
    db_path = r"C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM installers_haulers")
    haulers = cursor.fetchall()
    
    # 1. Print info about the PDFs
    for name, path in [("MWA Haulers", "mwa_haulers.pdf"), ("DPH Pumpers", "pumpers.pdf"), ("DPH Installers", "installers.pdf")]:
        try:
            doc = fitz.open(path)
            print(f"{name}: {len(doc)} pages")
        except Exception as e:
            print(f"Error opening {path}: {e}")
            
    print("\nMatching contractors in MWA Grease Haulers list...")
    mwa_doc = fitz.open("mwa_haulers.pdf")
    mwa_text = ""
    for page in mwa_doc:
        mwa_text += page.get_text("text") + "\n"
        
    print("\nMWA TEXT PREVIEW (First 1000 chars):")
    print(mwa_text[:1000])
    
    print("\nMatching contractors in DPH Certified Septic Pumpers list...")
    pump_doc = fitz.open("pumpers.pdf")
    pump_text = ""
    for page in pump_doc:
        pump_text += page.get_text("text") + "\n"
        
    print("\nDPH PUMP TEXT PREVIEW (First 1000 chars):")
    print(pump_text[:1000])
    
    # Let's search for some company names specifically
    for hid, hname in haulers:
        print(f"\nSearch for: {hname}")
        mwa_matches = search_pdf("mwa_haulers.pdf", hname)
        if mwa_matches:
            print("  MWA matches:")
            for p, l in mwa_matches[:3]:
                print(f"    Page {p}: {l.strip()}")
        p_matches = search_pdf("pumpers.pdf", hname)
        if p_matches:
            print("  DPH Pumper matches:")
            for p, l in p_matches[:3]:
                print(f"    Page {p}: {l.strip()}")

if __name__ == "__main__":
    main()
