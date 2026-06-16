import os, sqlite3

cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", "crawled_text", "01-gabar-georgia-closing-attorneys"))
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "directory.sqlite"))

cache_files = os.listdir(cache_dir)
ids = [f.split('.')[0] for f in cache_files if f.endswith('.txt')]

if ids:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    chunk_size = 900
    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i+chunk_size]
        placeholders = ",".join("?" for _ in chunk)
        c.execute(f"UPDATE attorneys SET specialties_crawled = 0 WHERE id IN ({placeholders}) AND faq_enriched IS NULL", chunk)
    conn.commit()
    conn.close()
    print(f"Reset specialties_crawled to 0 for {len(ids)} records.")
else:
    print("No cache files found.")
