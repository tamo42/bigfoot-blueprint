import sqlite3

conn = sqlite3.connect('cache/content_queue.db')
row = conn.execute("SELECT original_title, generated_markdown FROM articles WHERE niche_id='georgiagreasetrap' AND status='APPROVED' LIMIT 1").fetchone()

if row:
    with open('C:/Users/tamo4/git/bigfoot-sites/georgiagreasetrap.com/src/content/news/2026-06-16-restaurant-health-inspections.md', 'w', encoding='utf-8') as f:
        title = row[0].replace('"', '\\"')
        f.write(f"---\ntitle: \"{title}\"\npubDate: 2026-06-16T12:00:00Z\nauthor: \"Compliance Analyst\"\nsummary: \"Recent health inspections highlight the critical role of proper FOG management in avoiding costly restaurant closures.\"\n---\n\n{row[1]}")
    print("Exported grease trap article.")
