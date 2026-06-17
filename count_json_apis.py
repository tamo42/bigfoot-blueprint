import sqlite3

db_path = r'C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\data\water_well_directory.sqlite'
try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM well_contractors WHERE local_epa_water_alerts IS NULL;")
    epa = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM well_contractors WHERE local_groundwater_conditions IS NULL;")
    well_logs = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM well_contractors;")
    total = c.fetchone()[0]
    
    print(f"Total Records: {total}")
    print(f"EPA Pending: {epa}")
    print(f"Well Logs Pending: {well_logs}")
    
except Exception as e:
    print(f"Error: {e}")
