import sqlite3

db_path = r"c:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print("Tables:", tables)

for table in tables:
    tname = table[0]
    print(f"\nColumns for table {tname}:")
    c.execute(f"PRAGMA table_info({tname})")
    for col in c.fetchall():
        print(f"  {col[1]} ({col[2]})")
        
    c.execute(f"SELECT * FROM {tname} LIMIT 1")
    row = c.fetchone()
    if row:
        print(f"Sample row (keys & values):")
        # get column names
        c.execute(f"PRAGMA table_info({tname})")
        cols = [col[1] for col in c.fetchall()]
        for k, v in zip(cols, row):
            val_str = str(v)
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            print(f"  {k}: {val_str}")
            
conn.close()
