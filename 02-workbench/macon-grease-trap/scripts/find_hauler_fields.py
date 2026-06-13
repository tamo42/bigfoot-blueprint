import re

path = r"C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\pages\[slug].astro"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

matches = re.findall(r'hauler\.[a-zA-Z0-9_]+', content)
print("Found hauler fields:")
for m in sorted(list(set(matches))):
    print(f"  {m}")
