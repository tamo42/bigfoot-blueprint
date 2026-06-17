import os
import json
import sqlite3
import re

DB_PATH = os.path.join("cache", "content_queue.db")

# Map of niche IDs to target content directory paths
SITE_PATHS = {
    "gaclosinglawyers": r"c:\Users\tamo4\git\bigfoot-sites\gaclosinglawyers.com\src\content\news",
    "georgiagreasetrap": r"c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\content\news",
    "waterwelldrillers": r"c:\Users\tamo4\git\bigfoot-sites\uswelldrillers.com\src\content\news"
}

def clean_slug(title):
    # Remove source suffix like " - Barron's" or " - SCOTUSblog"
    clean_title = re.sub(r"\s+-\s+[\w\.\']+$", "", title)
    # Convert to lowercase and replace non-alphanumeric chars with hyphens
    slug = clean_title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug)
    return slug.strip("-")

def main():
    print("[START] Distributing approved news stories to directory sites...")
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, niche_id, original_title, generated_markdown 
        FROM articles 
        WHERE status = 'APPROVED'
    """)
    rows = cursor.fetchall()
    print(f"Found {len(rows)} approved articles in queue.")
    
    distributed_count = 0
    
    for row in rows:
        db_id, niche_id, title, markdown = row
        
        if niche_id not in SITE_PATHS:
            print(f"[SKIP] Unknown or unmapped niche_id '{niche_id}' for article: {title}")
            continue
            
        target_dir = SITE_PATHS[niche_id]
        
        # Verify target directory exists (the src folder should exist)
        src_dir = os.path.dirname(os.path.dirname(target_dir))
        if not os.path.exists(src_dir):
            print(f"[SKIP] Target site src directory does not exist: {src_dir}")
            continue
            
        os.makedirs(target_dir, exist_ok=True)
        
        slug = clean_slug(title)
        filepath = os.path.join(target_dir, f"{slug}.md")
        
        # Write the generated markdown to file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"[DISTRIBUTE] Pushed article to: {filepath}")
            distributed_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to write file {filepath}: {e}")
            
    print(f"\n[COMPLETE] Successfully distributed {distributed_count} articles across sites!")
    conn.close()

if __name__ == "__main__":
    main()
