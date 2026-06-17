import sqlite3
import re
import os

def clean_name(original_name):
    if not original_name:
        return ""
        
    name = str(original_name).strip()
    
    # Rule 1: Remove trailing lone letters (like 'F' at the end)
    name = re.sub(r'\s+[A-Za-z]$', '', name)
    
    # Rule 2: Remove trailing open parenthesis and anything after
    name = re.sub(r'\s*\([^)]*$', '', name)
    
    # Rule 3: Remove in-line area codes / numbers like (330)
    name = re.sub(r'\s*\(\d{3}\)\s*', ' ', name)
    
    # Rule 4: Remove trailing PO or PO Box or address fragments
    name = re.sub(r',\s*PO\s*BOX\s*\d*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r',\s*PO\s*$', '', name, flags=re.IGNORECASE)
    
    # Rule 5: Remove dates like 'May 12'
    name = re.sub(r'\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2}\s*', ' ', name)
    
    # Rule 6: Remove address fragments like '8638 N HIGH STREET'
    name = re.sub(r'\s*\d+\s+[A-Z\s]+STREET.*$', '', name, flags=re.IGNORECASE)
    
    # Rule 7: Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

import argparse

def main():
    parser = argparse.ArgumentParser(description="Clean messy names in the database.")
    parser.add_argument('--db', type=str, default=r'C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\data\water_well_directory.sqlite', help="Path to SQLite DB")
    args = parser.parse_args()
    
    db_path = args.db
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT id, name FROM well_contractors")
    rows = c.fetchall()
    
    updates = []
    log_lines = []
    
    for row in rows:
        row_id, original_name = row
        cleaned = clean_name(original_name)
        
        if cleaned and cleaned != original_name:
            updates.append((cleaned, row_id))
            log_lines.append(f"ID {row_id}:\n  Old: '{original_name}'\n  New: '{cleaned}'\n")
            
    # Apply updates
    c.executemany("UPDATE well_contractors SET name = ? WHERE id = ?", updates)
    conn.commit()
    conn.close()
    
    # Write log
    with open("cleaning_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Cleaned {len(updates)} records.\n\n")
        f.writelines(log_lines)
        
    print(f"Successfully cleaned {len(updates)} records. Review cleaning_log.txt for details.")

if __name__ == "__main__":
    main()
