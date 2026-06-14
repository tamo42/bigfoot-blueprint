import sqlite3

db_path = r"c:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("PRAGMA table_info(installers_haulers)")
cols = [col[1] for col in c.fetchall()]

c.execute("SELECT * FROM installers_haulers")
rows = c.fetchall()

regulatory_cols = [
    "id", "name", "license_no", "license_status", "permit_expiration", 
    "mwa_fog_compliance_code", "bibb_septage_permit_num", "eo_insurance_limit", 
    "coi_status", "pumper_certification_level", "disposal_site_partner"
]

print(" | ".join(regulatory_cols))
print("-" * 150)
for r in rows:
    row_dict = dict(zip(cols, r))
    vals = [str(row_dict[col]) for col in regulatory_cols]
    print(" | ".join(vals))

conn.close()
