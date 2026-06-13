import sys
import json
import sqlite3

if len(sys.argv) < 3:
    print("Usage: python update_db.py <slug> <json_data>")
    sys.exit(1)

slug = sys.argv[1]
data = json.loads(sys.argv[2])

db_path = r'C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite'

conn = sqlite3.connect(db_path)
c = conn.cursor()

set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
values = list(data.values())
values.append(slug)

query = f"UPDATE installers_haulers SET {set_clause} WHERE slug = ?"

c.execute(query, values)
conn.commit()

if c.rowcount == 0:
    print(f"Error: Slug '{slug}' not found.")
else:
    print(f"Successfully updated '{slug}'.")

conn.close()
