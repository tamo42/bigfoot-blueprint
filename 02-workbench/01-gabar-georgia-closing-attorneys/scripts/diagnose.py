import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "directory.sqlite"))
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", "crawled_text", "01-gabar-georgia-closing-attorneys"))

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM attorneys WHERE website_url IS NOT NULL AND website_url != 'NOT_FOUND' AND website_url != ''")
    total_valid_urls = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM attorneys WHERE faq_enriched IS NULL AND website_url IS NOT NULL AND website_url != 'NOT_FOUND' AND website_url != ''")
    total_unenriched = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM attorneys WHERE faq_enriched = 'FAILED'")
    total_failed_db = c.fetchone()[0]
    
    c.execute("SELECT website_url FROM attorneys WHERE faq_enriched IS NULL AND website_url IS NOT NULL AND website_url != 'NOT_FOUND' AND website_url != '' LIMIT 10")
    sample_urls = c.fetchall()
    
    conn.close()
    
    print(f"Total Valid URLs in DB: {total_valid_urls}")
    print(f"Total Unenriched (faq_enriched IS NULL): {total_unenriched}")
    print(f"Total Marked FAILED in DB: {total_failed_db}")
    print("\nSample of Unenriched URLs:")
    for url in sample_urls:
        print(f" - {url[0]}")
        
    if os.path.exists(CACHE_DIR):
        txt_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.txt')]
        failed_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.failed')]
        print(f"\nCache Directory Stats:")
        print(f" - .txt files: {len(txt_files)}")
        print(f" - .failed files: {len(failed_files)}")
    else:
        print("\nCache directory does not exist.")

if __name__ == '__main__':
    main()
