import sqlite3
import os
db_path = "02-workbench/georgia-closing-attorneys/data/directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT count(*) FROM attorneys WHERE appointments != '[]' AND appointments IS NOT NULL")
count = c.fetchone()[0]
print(f"Total enriched records: {count}")
