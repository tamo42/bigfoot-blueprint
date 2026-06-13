import json
import sqlite3

input_file = r'C:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\macon-grease-trap\data\pending_enrichment.json'
db_path = r'C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\data\directory.sqlite'

with open(input_file, 'r') as f:
    data = json.load(f)

conn = sqlite3.connect(db_path)
c = conn.cursor()

updated_count = 0

for row in data:
    slug = row['slug']
    name = row['name']
    city = row['city']
    fleet_size = row['fleet_size']
    
    # Skip the ones we already did manually
    if slug in ['birmingham-hide-tallow-co-inc', 'georgia-grease-plumbing', 'kaylors-septic-service-llc']:
        continue
        
    # Generate dynamic content based on fleet size
    if fleet_size >= 10:
        desc = f"<p><strong>{name}</strong> is a major regional player in the liquid waste and grease trap management industry, operating out of {city}, Georgia.</p><p>With a massive registered fleet of {fleet_size} commercial vehicles, they have the industrial capacity to handle high-volume accounts, municipal contracts, and emergency dispatch scenarios for large-scale commercial kitchens. Their scale makes them one of the most reliable choices for consistent compliance.</p>"
        best_for = "High-volume restaurants and multi-location chains"
        fee_structure = "Contract-based with volume discounts available"
        access = "Large-scale commercial fleet dispatch"
        q1 = "Why does their large fleet size matter?"
        a1 = f"Because {name} operates {fleet_size} state-registered vacuum trucks, they can virtually guarantee emergency response times and consistent scheduling without the delays typical of smaller operations."
    elif fleet_size >= 3:
        desc = f"<p><strong>{name}</strong> is a highly capable commercial plumbing and liquid waste hauler based in {city}, Georgia.</p><p>Operating a dedicated fleet of {fleet_size} FOG-permitted trucks, they strike the perfect balance between professional capacity and localized customer service. They are an excellent option for standard commercial kitchens and local restaurants needing reliable quarterly grease trap pumping.</p>"
        best_for = "Standard local restaurants and commercial kitchens"
        fee_structure = "Standard flat-rate pricing per service"
        access = f"Regional dispatch out of {city}"
        q1 = "Are they equipped for emergency backups?"
        a1 = f"Yes, with a fleet of {fleet_size} trucks, they have the operational redundancy to handle emergency dispatch calls in the {city} area while maintaining their regular maintenance routes."
    else:
        desc = f"<p><strong>{name}</strong> is a local, independent liquid waste management provider operating in {city}, Georgia.</p><p>As a specialized independent hauler, they provide highly personalized customer service and flexible scheduling for commercial grease trap pumping. They hold verified FOG (Fats, Oils, and Grease) permits, ensuring full environmental compliance for local food service establishments.</p>"
        best_for = "Local independent restaurants and small kitchens"
        fee_structure = "Flat rate based on trap gallon capacity"
        access = f"Local dispatch out of {city}, GA"
        q1 = "Why should I hire an independent local hauler?"
        a1 = f"Independent haulers like {name} often have lower corporate overhead, which can result in highly competitive pricing. Plus, you usually deal directly with the owner for scheduling."

    # Standard Q2 for all
    q2 = f"Is {name} properly licensed to haul grease?"
    a2 = f"Yes, {name} is actively registered with the state and holds unique FOG (Fats, Oils, and Grease) transport permits, making them fully compliant with commercial wastewater regulations."

    update_data = {
        "listing_content": desc,
        "quickfact_best_for": best_for,
        "quickfact_primary_items": "Grease Trap Pumping, Liquid Waste Disposal",
        "quickfact_fee_structure": fee_structure,
        "quickfact_access": access,
        "qa_1_question": q1,
        "qa_1_answer": a1,
        "qa_2_question": q2,
        "qa_2_answer": a2
    }
    
    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
    values = list(update_data.values())
    values.append(slug)
    query = f"UPDATE installers_haulers SET {set_clause} WHERE slug = ?"
    
    c.execute(query, values)
    updated_count += 1

conn.commit()
print(f"Batch enrichment completed. Updated {updated_count} companies.")
conn.close()
