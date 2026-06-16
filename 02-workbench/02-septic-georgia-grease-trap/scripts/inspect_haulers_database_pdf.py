import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    pdf_path = os.path.join(data_dir, "2026-approved-commercial-haulers-data-base.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return
        
    doc = fitz.open(pdf_path)
    print(f"PDF Opened: {pdf_path}")
    print(f"Total Pages: {len(doc)}")
    
    # Print the first 2000 characters of page 1 text
    page1_text = doc[0].get_text("text")
    print("\n--- Page 1 Raw Text (truncated) ---")
    print(page1_text[:2000])
    
    # Search for names matching our local contractors in the entire PDF
    companies = [
        "Underground Septic",
        "A-1 Sanitation",
        "Fast Flow",
        "Stewart Septic",
        "Septic Tank Pros",
        "Big Daddy",
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
    
    print("\n--- Search Results in PDF ---")
    for company in companies:
        found_matches = []
        for i in range(len(doc)):
            text = doc[i].get_text("text")
            lines = text.split("\n")
            for line in lines:
                if company.lower() in line.lower():
                    found_matches.append((i+1, line.strip()))
        if found_matches:
            print(f"'{company}':")
            for page, line in found_matches[:5]:
                print(f"  Page {page}: {line}")

if __name__ == "__main__":
    main()
