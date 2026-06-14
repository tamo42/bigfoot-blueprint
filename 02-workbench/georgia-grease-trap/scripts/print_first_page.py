import fitz

def dump_page(pdf_path):
    print(f"\n==========================================")
    print(f"RAW TEXT FOR {pdf_path} PAGE 1")
    print(f"==========================================")
    doc = fitz.open(pdf_path)
    if len(doc) > 0:
        print(doc[0].get_text("text"))
        
dump_page("02-workbench/macon-grease-trap/data/mwa_haulers.pdf")
dump_page("02-workbench/macon-grease-trap/data/pumpers.pdf")
