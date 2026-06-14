import fitz

doc = fitz.open("02-workbench/macon-grease-trap/data/installers.pdf")
if len(doc) > 0:
    print(doc[0].get_text("text"))
