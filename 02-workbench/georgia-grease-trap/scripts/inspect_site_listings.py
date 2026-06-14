import sqlite3

db_path = r"c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, name, listing_name, mwa_fog_compliance_code, bibb_septage_permit_num FROM installers_haulers")
rows = c.fetchall()

print(f"{'ID':<3} | {'Name':<45} | {'Listing Name':<45} | {'FOG Code':<15} | {'Septic Code':<15}")
print("-" * 130)
for r in rows:
    print(f"{r[0]:<3} | {r[1]:<45} | {str(r[2]):<45} | {str(r[3]):<15} | {str(r[4]):<15}")

conn.close()
