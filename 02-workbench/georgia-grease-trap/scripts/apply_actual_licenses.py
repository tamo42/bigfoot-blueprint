import sqlite3

def main():
    db_path = r"c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Step 1: Clear all synthetic/placeholder compliance codes and septage permit numbers
    print("Clearing synthetic/placeholder permit codes...")
    c.execute("""
        UPDATE installers_haulers
        SET mwa_fog_compliance_code = NULL,
            bibb_septage_permit_num = NULL
    """)
    conn.commit()

    # Step 2: Set actual permit numbers for verified matches
    print("Setting actual permit numbers for matched commercial waste haulers...")
    
    # 1. Ricky Heath Plumbing, Heating, & Cooling (ID: 13) -> FOG036
    c.execute("""
        UPDATE installers_haulers
        SET mwa_fog_compliance_code = 'FOG036'
        WHERE id = 13
    """)

    # 2. Safety-Kleen Systems (ID: 15) -> FOG114-278
    c.execute("""
        UPDATE installers_haulers
        SET mwa_fog_compliance_code = 'FOG114-278'
        WHERE id = 15
    """)

    # 3. AmeriPro Environmental Services (ID: 16) -> FOG500
    c.execute("""
        UPDATE installers_haulers
        SET mwa_fog_compliance_code = 'FOG500'
        WHERE id = 16
    """)

    conn.commit()
    print("Database updated successfully!")

    # Verify changes
    c.execute("SELECT id, name, mwa_fog_compliance_code, bibb_septage_permit_num FROM installers_haulers")
    rows = c.fetchall()
    print("\n--- Updated Database Table ---")
    for r in rows:
        print(f"ID: {r[0]:<2} | {r[1]:<45} | FOG: {str(r[2]):<12} | Septic: {str(r[3])}")

    conn.close()

if __name__ == '__main__':
    main()
