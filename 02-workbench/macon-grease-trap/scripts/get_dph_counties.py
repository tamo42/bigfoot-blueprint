import fitz

def get_county_for_match(pdf_path, comp_name):
    doc = fitz.open(pdf_path)
    current_county = None
    for page_idx in range(len(doc)):
        text = doc[page_idx].get_text("text")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # In DPH lists, counties are printed alone, followed by the companies in that county.
        # We need to trace the county name.
        # Counties are usually: Appling, Atkinson, Bacon, Baldwin, Banks, Barrow, Bartow, Ben Hill, Berrien, Bibb, Bleckley, Brantley, Brooks, Bryan, Bulloch, Burke, Butts, Calhoun, Camden, Candler, Carroll, Catoosa, Charlton, Chatham, Chattahoochee, Chattooga, Cherokee, Clarke, Clay, Clayton, Clinch, Cobb, Coffee, Colquitt, Columbia, Cook, Coweta, Crawford, Crisp, Dade, Dawson, Decatur, DeKalb, Dodge, Dooly, Dougherty, Douglas, Early, Echols, Effingham, Elbert, Emanuel, Evans, Fannin, Fayette, Floyd, Forsyth, Franklin, Fulton, Gilmer, Glascock, Glynn, Gordon, Grady, Greene, Gwinnett, Habersham, Hall, Hancock, Haralson, Harris, Hart, Heard, Henry, Houston, Irwin, Jackson, Jasper, Jeff Davis, Jefferson, Jenkins, Johnson, Jones, Lamar, Lanier, Laurens, Lee, Liberty, Lincoln, Long, Lowndes, Lumpkin, Macon, Madison, Marion, McDuffie, McIntosh, Meriwether, Miller, Mitchell, Monroe, Montgomery, Morgan, Murray, Muscogee, Newton, Oconee, Oglethorpe, Paulding, Peach, Pickens, Pierce, Pike, Polk, Pulaski, Putnam, Quitman, Rabun, Randolph, Richmond, Rockdale, Schley, Screven, Seminole, Spalding, Stephens, Stewart, Sumter, Talbot, Taliaferro, Tattnall, Taylor, Telfair, Terrell, Thomas, Tift, Toombs, Towns, Treutlen, Troup, Turner, Twiggs, Union, Upson, Walker, Walton, Ware, Warren, Washington, Wayne, Webster, Wheeler, White, Whitfield, Wilcox, Wilkes, Wilkinson, Worth.
        
        known_counties = {
            "Appling", "Atkinson", "Bacon", "Baldwin", "Banks", "Barrow", "Bartow", "Ben Hill", "Berrien", "Bibb",
            "Bleckley", "Brantley", "Brooks", "Bryan", "Bulloch", "Burke", "Butts", "Calhoun", "Camden", "Candler",
            "Carroll", "Catoosa", "Charlton", "Chatham", "Chattahoochee", "Chattooga", "Cherokee", "Clarke", "Clay",
            "Clayton", "Clinch", "Cobb", "Coffee", "Colquitt", "Columbia", "Cook", "Coweta", "Crawford", "Crisp",
            "Dade", "Dawson", "Decatur", "DeKalb", "Dodge", "Dooly", "Dougherty", "Douglas", "Early", "Echols",
            "Effingham", "Elbert", "Emanuel", "Evans", "Fannin", "Fayette", "Floyd", "Forsyth", "Franklin", "Fulton",
            "Gilmer", "Glascock", "Glynn", "Gordon", "Grady", "Greene", "Gwinnett", "Habersham", "Hall", "Hancock",
            "Haralson", "Harris", "Hart", "Heard", "Henry", "Houston", "Irwin", "Jackson", "Jasper", "Jeff Davis",
            "Jefferson", "Jenkins", "Johnson", "Jones", "Lamar", "Lanier", "Laurens", "Lee", "Liberty", "Lincoln",
            "Long", "Lowndes", "Lumpkin", "Macon", "Madison", "Marion", "McDuffie", "McIntosh", "Meriwether", "Miller",
            "Mitchell", "Monroe", "Montgomery", "Morgan", "Murray", "Muscogee", "Newton", "Oconee", "Oglethorpe",
            "Paulding", "Peach", "Pickens", "Pierce", "Pike", "Polk", "Pulaski", "Putnam", "Quitman", "Rabun",
            "Randolph", "Richmond", "Rockdale", "Schley", "Screven", "Seminole", "Spalding", "Stephens", "Stewart",
            "Sumter", "Talbot", "Taliaferro", "Tattnall", "Taylor", "Telfair", "Terrell", "Thomas", "Tift", "Toombs",
            "Towns", "Treutlen", "Troup", "Turner", "Twiggs", "Union", "Upson", "Walker", "Walton", "Ware", "Warren",
            "Washington", "Wayne", "Webster", "Wheeler", "White", "Whitfield", "Wilcox", "Wilkes", "Wilkinson", "Worth"
        }
        
        for line in lines:
            if line in known_counties:
                current_county = line
            if comp_name.lower() in line.lower():
                print(f"Company: {comp_name} | Found under County: {current_county} | Page: {page_idx + 1}")
                return current_county
    return None

pumper_pdf = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\pumpers.pdf"
installer_pdf = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\installers.pdf"

comps = [
    "Underground Septic Services, LLC",
    "Stewart Septic Services, LLC",
    "Big Daddy's Septic Service",
    "Asap Septic LLC",
    "Kitchens & Young Septic Service",
    "Bowen's Septic Tank Service",
    "Ricky Heath Plumbing",
    "Environmental Remedies, LLC",
    "JTL Sitework & Septic Services, LLC"
]

print("=== Pumpers PDF Counties ===")
for c in comps:
    get_county_for_match(pumper_pdf, c)

print("\n=== Installers PDF Counties ===")
for c in comps:
    get_county_for_match(installer_pdf, c)
