import sqlite3

db_path = r"c:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, name, listing_type, admin_category FROM installers_haulers")
rows = c.fetchall()

print(f"{'ID':<3} | {'Name':<45} | {'Listing Type':<25} | {'Admin Category'}")
print("-" * 100)
for r in rows:
    print(f"{r[0]:<3} | {r[1]:<45} | {str(r[2]):<25} | {str(r[3])}")

conn.close()
