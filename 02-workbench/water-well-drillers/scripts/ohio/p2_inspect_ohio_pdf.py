import os
import pypdf
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import p3_utils as utils

pdf_path = utils.resolve_path(r"cache\ohio_registered_pws_contractors.pdf")
output_path = utils.resolve_path(r"02-workbench\water-well-drillers\ohio_pdf_text_sample.txt")

def main():
    if not os.path.exists(pdf_path):
        print(f"[-] Error: File not found: {pdf_path}")
        return

    print(f"[*] Reading PDF: {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"[+] Total Pages: {total_pages}")
        
        sample_text = []
        pages_to_extract = min(5, total_pages)
        for i in range(pages_to_extract):
            print(f"[*] Extracting layout from Page {i+1}...")
            page = reader.pages[i]
            text = page.extract_text(extraction_mode="layout")
            sample_text.append(f"--- PAGE {i+1} ---")
            sample_text.append(text)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(sample_text))
            
        print(f"[+] Diagnostic text layout saved to {output_path}")
        
    except Exception as e:
        print(f"[-] Error reading PDF: {e}")

if __name__ == "__main__":
    main()
