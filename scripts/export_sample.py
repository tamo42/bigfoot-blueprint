import sqlite3
import os

conn = sqlite3.connect('cache/content_queue.db')
row = conn.execute("SELECT niche_id, original_title, generated_markdown FROM articles WHERE status='APPROVED'").fetchone()

if row:
    niche_id, title, markdown = row
    with open('cache/sample_post.md', 'w', encoding='utf-8') as f:
        f.write(f"---\ntitle: {title}\n---\n\n{markdown}")
    print(f"Exported {niche_id} post to cache/sample_post.md")
else:
    print("No approved posts found.")
