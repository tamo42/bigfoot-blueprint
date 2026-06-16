import os
import re
import sqlite3

# Resolve database path and get valid slugs
db_path = r"c:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src\data\directory.sqlite"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM installers_haulers WHERE post_status = 'publish'")
db_names = [row[0] for row in c.fetchall()]
conn.close()

# Slugify function matching src/data/db.js
def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]+', '', text)
    text = re.sub(r'\-\-+', '-', text)
    text = re.sub(r'^-+', '', text)
    text = re.sub(r'-+$', '', text)
    return text

# In db.js, slugs are resolved for duplicates by adding city names if duplicate.
# But since we have unique names here or we want to match our Astro compiled routes,
# let's list the actual routes we saw in the npm run build output:
valid_routes = {
    "/",
    "/georgia",
    "/macon-bibb",
    "/houston",
    "/peach",
    "/jones",
    "/monroe",
    "/baldwin",
    "/laurens",
    "/macon-grease-trap-requirements",
    "/macon-septic-pumping-guide",
    "/ricky-heath-plumbing-heating-cooling",
    "/safety-kleen-systems",
    "/ameripro-environmental-services",
    "/watson-plumbing",
    "/marlers-plumbing-services-llc",
}

src_dir = r"C:\Users\tamo4\git\bigfoot-sites\georgiagreasetrap.com\src"
astro_files = []
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith((".astro", ".md", ".js")):
            astro_files.append(os.path.join(root, f))

print(f"Scanning {len(astro_files)} files in src/ for links...")
print(f"Valid routes loaded: {len(valid_routes)}")

broken_count = 0
for file_path in astro_files:
    rel_path = os.path.relpath(file_path, src_dir)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Match href="..." or href='...'
    # E.g. href="/listings/underground"
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', content)
    
    # Also find dynamically generated hrefs if they have a clear pattern
    # For example, in Astro templates: href={`/${hauler.slug}`}
    dynamic_hrefs = re.findall(r'href=\{\`([^\`]+)\`\}', content)
    for dh in dynamic_hrefs:
        # If it matches something like /${hauler.slug}, it's dynamic
        hrefs.append(dh)

    for href in hrefs:
        # Ignore external links, mailto, tel, and anchor-only links
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        
        # Strip trailing slash or query params if any
        clean_href = href.split("?")[0].split("#")[0].rstrip("/")
        if not clean_href:
            clean_href = "/"
            
        # If the href has template variables like ${hauler.slug}, we skip detailed verification,
        # but check if the base path pattern is correct (e.g. /${hauler.slug} or /listings/${hauler.slug})
        if "${" in clean_href:
            # Check if there is an old path segment like /listings/ or /hauler/ or /installer/
            if "/listings/" in clean_href or "/hauler/" in clean_href or "/installer/" in clean_href:
                print(f"Broken/Old Dynamic Link in [src/{rel_path}]: href='{href}'")
                broken_count += 1
            continue
            
        if clean_href not in valid_routes:
            print(f"Broken/Old Link in [src/{rel_path}]: href='{href}' (resolved: '{clean_href}')")
            broken_count += 1

print(f"\nScan completed. Found {broken_count} potentially broken/outdated internal links.")
