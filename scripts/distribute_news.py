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
    
    # 1. Add 'published' column if it does not exist
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN published INTEGER DEFAULT 0")
        conn.commit()
        print("Schema migrated: added 'published' column.")
    except sqlite3.OperationalError:
        # Column already exists
        pass
        
    distributed_count = 0
    
    # Process each niche individually to find the single best story of the day
    for niche_id, target_dir in SITE_PATHS.items():
        print(f"\nEvaluating queue for niche '{niche_id}'...")
        
        # Verify target directory exists (the src folder should exist)
        src_dir = os.path.dirname(os.path.dirname(target_dir))
        if not os.path.exists(src_dir):
            print(f"[SKIP] Target site src directory does not exist: {src_dir}")
            continue
            
        cursor.execute("""
            SELECT id, original_title, generated_markdown, editor_score_json 
            FROM articles 
            WHERE status = 'APPROVED' AND published = 0 AND niche_id = ?
        """, (niche_id,))
        
        candidates = cursor.fetchall()
        if not candidates:
            print(f"No unpublished approved articles found for {niche_id}.")
            continue
            
        best_candidate = None
        max_score = -1
        
        for cand in candidates:
            db_id, title, markdown, score_json_str = cand
            score = 0
            try:
                score_data = json.loads(score_json_str)
                score = score_data.get("total_score", 0)
            except Exception:
                pass
            
            if score > max_score:
                max_score = score
                best_candidate = (db_id, title, markdown)
                
        if best_candidate:
            db_id, title, markdown = best_candidate
            os.makedirs(target_dir, exist_ok=True)
            slug = clean_slug(title)
            filepath = os.path.join(target_dir, f"{slug}.md")
            
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(markdown)
                print(f"[DISTRIBUTE] Pushed article (Score: {max_score}) to: {filepath}")
                
                # Mark as published in DB
                cursor.execute("UPDATE articles SET published = 1 WHERE id = ?", (db_id,))
                conn.commit()
                distributed_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to write file {filepath}: {e}")
                
    print(f"\n[COMPLETE] Successfully distributed {distributed_count} articles across sites!")
    conn.close()

if __name__ == "__main__":
    main()
