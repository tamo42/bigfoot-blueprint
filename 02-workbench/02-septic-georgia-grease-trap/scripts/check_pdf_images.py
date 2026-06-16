import fitz

doc = fitz.open("02-workbench/02-septic-georgia-grease-trap/data/mwa_haulers.pdf")
page = doc[0]
il = page.get_images()
print("Images list:", il)
print("Page rect:", page.rect)
