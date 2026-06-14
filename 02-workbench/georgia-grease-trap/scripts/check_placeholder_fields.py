import sqlite3

db_path = r"c:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get all column names
c.execute("PRAGMA table_info(installers_haulers)")
cols = [col[1] for col in c.fetchall()]

c.execute("SELECT * FROM installers_haulers")
rows = c.fetchall()

print("Scanning for placeholders...")
for r in rows:
    row_dict = dict(zip(cols, r))
    name = row_dict["name"]
    for k, v in row_dict.items():
        v_str = str(v)
        if v is not None and ("2026-" in v_str or "FOG-20" in v_str or "SEPT-20" in v_str or "MWA-" in v_str or "BIBB-" in v_str):
            print(f"Row: {name} | Column: {k} | Value: {v}")

conn.close()
