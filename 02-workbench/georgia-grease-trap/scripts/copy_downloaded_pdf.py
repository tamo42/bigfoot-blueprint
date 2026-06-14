import shutil
import os

src = r"C:\Users\tamo4\Downloads\2026-approved-commercial-haulers-data-base.pdf"
dst = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\2026-approved-commercial-haulers-data-base.pdf"

if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"Successfully copied PDF from {src} to {dst}")
else:
    print(f"Error: Source PDF not found at {src}")
