import fitz

def inspect_pdf(name, path):
    print(f"\n=== Inspecting {name} ({path}) ===")
    doc = fitz.open(path)
    text = doc[0].get_text("text")
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for idx, l in enumerate(lines[:30]):
        print(f"Line {idx+1}: {l}")

inspect_pdf("DPH Pumpers", r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\pumpers.pdf")
inspect_pdf("DPH Installers", r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\installers.pdf")
inspect_pdf("MWA Haulers", r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-grease-trap\data\mwa_haulers.pdf")
