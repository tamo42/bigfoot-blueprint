import fitz
import os
import re

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    pdf_path = os.path.join(data_dir, "2026-approved-commercial-haulers-data-base.pdf")
    
    doc = fitz.open(pdf_path)
    print(f"Total Pages: {len(doc)}")
    
    for page_idx in range(len(doc)):
        text = doc[page_idx].get_text("text")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        print(f"\n--- Page {page_idx + 1} Parsing ---")
        for idx, line in enumerate(lines):
            if re.match(r'^FOG\d+-\d+$', line):
                print(f"FOG ID: {line}")
                # Print lines before it to see the offset
                start = max(0, idx - 6)
                for i in range(start, idx + 1):
                    offset = idx - i
                    print(f"  Offset -{offset}: {lines[i]}")
                print("-" * 30)

if __name__ == "__main__":
    main()
