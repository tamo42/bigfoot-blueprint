import json
import sqlite3

slug = "kaylors-septic-service-llc"
data = {
  "name": "Kaylors Septic Service LLC",
  "website_url": "",
  "phone_number": "(770) 597-3241",
  "address": "110 Pine Ridge Road NW, White, GA 30184",
  "listing_content": "<p><strong>Kaylors Septic Service LLC</strong> is a local septic and liquid waste management provider based in White, Georgia. Operating as an independent hauler, they service commercial and residential clients in the surrounding counties.</p><p>Because they are a smaller, independent business, they often provide highly personalized customer service and flexible scheduling for commercial grease trap pumping and residential septic tank maintenance. They hold a verified FOG (Fats, Oils, and Grease) permit, ensuring that all commercial kitchen waste is transported and disposed of according to state environmental regulations.</p>",
  "quickfact_best_for": "Local independent restaurants and residential septic",
  "quickfact_primary_items": "Grease Trap Pumping, Septic Tank Pumping",
  "quickfact_fee_structure": "Flat rate per pump based on gallon capacity",
  "quickfact_access": "Local dispatch out of White, GA",
  "qa_1_question": "Do they provide residential septic services as well?",
  "qa_1_answer": "Yes, as a specialized septic service, they can handle both residential septic systems and commercial restaurant grease traps, making them a versatile choice for property managers.",
  "qa_2_question": "Why should I hire a local independent hauler?",
  "qa_2_answer": "Independent haulers like Kaylors Septic Service often have lower overhead than massive national aggregators, which can result in more competitive pricing and direct access to the owner for scheduling."
}

db_path = r'C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()

set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
values = list(data.values())
values.append(slug)
query = f"UPDATE installers_haulers SET {set_clause} WHERE slug = ?"

c.execute(query, values)
conn.commit()
print(f"Updated {c.rowcount} rows for {slug}")
conn.close()
