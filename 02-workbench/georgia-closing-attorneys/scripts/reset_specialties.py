import os, sqlite3

cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", "crawled_text", "georgia-closing-attorneys"))
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "directory.sqlite"))

cache_files = os.listdir(cache_dir)
ids = [f.split('.')[0] for f in cache_files if f.endswith('.txt')]

if ids:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    placeholders = ",".join("?" for _ in ids)
    c.execute(f"UPDATE attorneys SET specialties_crawled = 0 WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()
    print(f"Reset specialties_crawled to 0 for {len(ids)} records.")
else:
    print("No cache files found.")
