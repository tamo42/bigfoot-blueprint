import os
import sqlite3

DB_PATH = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\01-gabar-georgia-closing-attorneys\data\directory.sqlite"
CACHE_DIR = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\01-gabar-georgia-closing-attorneys\cache\crawled_text\01-gabar-georgia-closing-attorneys"

def count_tokens():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Select records that haven't been enriched yet (faq_enriched IS NULL)
    c.execute("""
        SELECT id 
        FROM attorneys 
        WHERE faq_enriched IS NULL 
          AND website_url IS NOT NULL 
          AND website_url != 'NOT_FOUND'
    """)
    rows = c.fetchall()
    conn.close()

    total_words = 0
    valid_files = 0
    
    for row in rows:
        row_id = row[0]
        filepath = os.path.join(CACHE_DIR, f"{row_id}.txt")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                words = len(content.split())
                total_words += words
                valid_files += 1

    if valid_files == 0:
        print("No remaining cache files found.")
        return

    avg_words = total_words / valid_files
    # Rough estimation: 1 token ~= 0.75 words, so tokens = words / 0.75 or words * 1.33
    avg_tokens = avg_words * 1.33
    total_tokens = total_words * 1.33

    print(f"Remaining Records to Process: {len(rows)}")
    print(f"Records with valid Cache Files: {valid_files}")
    print(f"==========================================")
    print(f"Average Words per Site:  {avg_words:,.0f} words")
    print(f"Average Tokens per Site: ~{avg_tokens:,.0f} tokens")
    print(f"==========================================")
    print(f"Total Word Count:        {total_words:,.0f} words")
    print(f"Total Token Count:       ~{total_tokens:,.0f} tokens")

if __name__ == "__main__":
    count_tokens()
