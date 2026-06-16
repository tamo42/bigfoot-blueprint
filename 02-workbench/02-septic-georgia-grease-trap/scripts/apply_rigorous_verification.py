import sqlite3

def main():
    db_path = r"c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    grease_img = "https://images.unsplash.com/photo-1581094288338-2314dddb7ecc?w=800"
    septic_img = "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800"

    # Define the 20 listings and their verified statuses
    # 0 = Unverified/Grease-only, 1 = Septic Pumper & Installer, 2 = Pumper only, 3 = Installer only
    listings_status = {
        1: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # Underground Septic
        2: {"type": "septic", "dph": None, "status": "Unverified"}, # A-1 Sanitation
        3: {"type": "septic", "dph": None, "status": "Unverified"}, # Fast Flow
        4: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # Stewart
        5: {"type": "septic", "dph": None, "status": "Unverified"}, # Septic Tank Pros
        6: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # Big Daddy
        7: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # ASAP Septic (WR)
        8: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # Kitchens & Young
        9: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # Bowen's
        10: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # ASAP Septic (Macon)
        11: {"type": "septic", "dph": None, "status": "Unverified"}, # A1 Pumping
        12: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"}, # ASAP Septic (Perry)
        13: {"type": "grease", "dph": "Pumper & Installer", "status": "Active"}, # Ricky Heath (Dual)
        14: {"type": "grease", "dph": "Pumper", "status": "Active"}, # Environmental Remedies (Pumper)
        15: {"type": "grease", "dph": None, "status": "Active FOG Transporter"}, # Safety-Kleen
        16: {"type": "grease", "dph": None, "status": "Active FOG Transporter"}, # AmeriPro
        17: {"type": "septic", "dph": "Installer", "status": "Active"}, # Mr. Rooter (Installer)
        18: {"type": "grease", "dph": None, "status": "Unverified"}, # SERVPRO
        19: {"type": "grease", "dph": None, "status": "Unverified"}, # Extreme Clean
        20: {"type": "septic", "dph": "Pumper & Installer", "status": "Active"} # JTL Sitework
    }

    print("Updating listings with verified DPH and FOG statuses...")
    for lid, info in listings_status.items():
        listing_type = "septic_pumping_service" if info["type"] == "septic" else "grease_trap_cleaning"
        img_url = septic_img if info["type"] == "septic" else grease_img
        
        # Determine DPH certification text
        if info["dph"] == "Pumper & Installer":
            dph_cert = "DPH Certified Septic Pumper & Installer"
        elif info["dph"] == "Pumper":
            dph_cert = "DPH Certified Septic Pumper"
        elif info["dph"] == "Installer":
            dph_cert = "DPH Certified Septic Installer"
        else:
            dph_cert = None
            
        license_status = info["status"]
        
        # If active, disposal site is MWA facility; otherwise None
        disposal_site = "Authorized Macon Water Authority Treatment Facility" if license_status in ["Active", "Active FOG Transporter"] else None
        
        c.execute("""
            UPDATE installers_haulers
            SET listing_type = ?,
                admin_category = ?,
                listing_img = ?,
                pumper_certification_level = ?,
                license_status = ?,
                disposal_site_partner = ?,
                eo_insurance_limit = NULL,
                coi_status = 'Unverified'
            WHERE id = ?
        """, (listing_type, listing_type, img_url, dph_cert, license_status, disposal_site, lid))

    conn.commit()
    print("Database updated successfully with actual data!")

    # Verify changes
    c.execute("SELECT id, name, listing_type, pumper_certification_level, license_status, mwa_fog_compliance_code FROM installers_haulers")
    rows = c.fetchall()
    print("\n--- Verified Listings in Database ---")
    for r in rows:
        print(f"ID: {r[0]:<2} | {r[1]:<45} | Type: {r[2]:<22} | DPH Cert: {str(r[3]):<38} | Status: {r[4]:<22} | FOG: {str(r[5])}")

    conn.close()

if __name__ == '__main__':
    main()
