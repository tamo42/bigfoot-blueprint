import fitz

doc = fitz.open(r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\2026-approved-commercial-haulers-data-base.pdf")

print("Searching for 'remedies'...")
for page_idx in range(len(doc)):
    text = doc[page_idx].get_text("text")
    if "remedies" in text.lower():
        print(f"Found 'remedies' on page {page_idx + 1}:")
        print(text)

print("\nSearching for phone number parts...")
for page_idx in range(len(doc)):
    text = doc[page_idx].get_text("text")
    if "627" in text or "5931" in text:
        print(f"Found phone match on page {page_idx + 1}:")
        print(text)

print("\nDone searching.")
