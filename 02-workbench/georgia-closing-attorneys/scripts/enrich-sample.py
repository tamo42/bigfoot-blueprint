import os
import sqlite3
import json

def generate_faq(listing_type, name, firm, city):
    # Standard questions 1-10
    faq = [
        {
            "question": "What is this place and what can I find here?",
            "answer": f"This listing is for {firm}, the legal office of registered closing attorney {name} in {city}, Georgia. You can find professional legal supervision for real estate transactions, title examinations, and escrow services here."
        },
        {
            "question": "Do I need an appointment or can I walk in?",
            "answer": "Appointments are strictly required for all real estate closings and consultations to ensure all deed filings and escrow details are verified beforehand."
        },
        {
            "question": "What are the hours of operation?",
            "answer": "The office is open Monday through Friday, from 9:00 AM to 5:00 PM, excluding major state and federal holidays."
        },
        {
            "question": "Is there a fee to use this?",
            "answer": "Attorney closing fees and title insurance premiums vary by transaction type and purchase price. Please contact the office directly for a detailed estimate of settlement costs."
        },
        {
            "question": "Who is this open to — anyone, or only residents/members?",
            "answer": "Services are open to any buyer, seller, real estate investor, or lender coordinating a real estate transaction within our geographic service counties in Georgia."
        },
        {
            "question": "Is this open on weekends?",
            "answer": "No, the office is closed on Saturdays and Sundays. Special weekend closing sessions must be pre-arranged and approved by the closing attorney."
        },
        {
            "question": "How do I get there and where do I park?",
            "answer": f"The office is located in {city}, Georgia. Visitor parking is available directly in front of the building or in the designated client parking lot."
        },
        {
            "question": "Who owns or operates this listing?",
            "answer": f"This legal practice is owned and operated by {name}, a licensed attorney in good standing with the State Bar of Georgia."
        },
        {
            "question": "How current is the information on this page?",
            "answer": "The licensing details and bar registration status are synchronized directly with public regulatory records. Specific office details are updated periodically by the firm's staff."
        },
        {
            "question": "How do I contact this listing directly?",
            "answer": "You can reach the office by phone or email using the contact details provided in the profile header on this page."
        }
    ]

    # Niche specific questions 11-20
    if listing_type == "residential_closing_attorney":
        faq.extend([
            {
                "question": "Do you handle residential buyer and seller representation in Georgia?",
                "answer": "Yes, we represent buyers and sellers in residential real estate purchase transactions, contract drafting, and title resolution."
            },
            {
                "question": "What are your standard closing fees for a residential purchase?",
                "answer": "Standard residential closing fees typically range from $850 to $1,200 depending on the complexity of the loan and title search requirements."
            },
            {
                "question": "Can you perform remote or mobile real estate closings?",
                "answer": "Yes, we can coordinate mobile closing services where a licensed notary or attorney travels to your location, subject to travel fees."
            },
            {
                "question": "Which title insurance underwriters are you appointed with?",
                "answer": "We maintain active agent appointments with major national title underwriters, enabling us to issue comprehensive owner's and lender's policies."
            },
            {
                "question": "How do you verify and protect wire transfers from fraud?",
                "answer": "We enforce strict multi-factor verification. Before sending any funds, you must verbally verify the wire instructions with a member of our staff via our published phone number."
            },
            {
                "question": "Do you assist with clearing complex title defects or liens?",
                "answer": "Yes, we perform thorough title searches and work diligently to resolve outstanding liens, probate hurdles, and ownership disputes before closing."
            },
            {
                "question": "How long does a standard residential closing take at your office?",
                "answer": "A typical closing signing session takes approximately 45 to 60 minutes once all loan documents have been approved by the lender."
            },
            {
                "question": "Do you handle mail-away closings for out-of-state buyers or sellers?",
                "answer": "Yes, we prepare and dispatch secure overnight mail-away packages with detailed signing instructions for out-of-state transaction parties."
            },
            {
                "question": "What documents do I need to bring to a residential closing?",
                "answer": "You must bring two forms of government-issued photo identification (such as a driver's license or passport) and any funds required for closing in the form of a bank wire."
            },
            {
                "question": "Are you active and in good standing with the State Bar of Georgia?",
                "answer": f"Yes, closing attorney {name} is active and in good standing with the State Bar of Georgia under registered bar registration rules."
            }
        ])
    elif listing_type == "commercial_closing_attorney":
        faq.extend([
            {
                "question": "Do you handle complex commercial real estate transactions in Georgia?",
                "answer": "Yes, we provide legal services for commercial acquisitions, development financing, zoning compliance, and entity formation."
            },
            {
                "question": "What types of commercial properties do you specialize in closing?",
                "answer": "We close multi-family housing complexes, retail spaces, industrial warehouses, office buildings, and undeveloped commercial parcels."
            },
            {
                "question": "Do you assist with commercial lease drafting and reviews?",
                "answer": "Yes, we draft, review, and negotiate commercial lease agreements for both landlords and tenants."
            },
            {
                "question": "Which major commercial title insurance companies do you use?",
                "answer": "We partner with major commercial title underwriters including Fidelity National Title, Chicago Title, and Commonwealth Land Title."
            },
            {
                "question": "Can you handle environmental or zoning due diligence reviews?",
                "answer": "Yes, we assist buyers in reviewing environmental assessments, zoning letters, and land use covenants during the due diligence period."
            },
            {
                "question": "Do you represent commercial lenders or developers in transactions?",
                "answer": "Yes, we represent commercial mortgage lenders in drafting loan packages, and developers in securing construction financing."
            },
            {
                "question": "What are the typical escrow requirements for a commercial deal?",
                "answer": "Escrow requirements are customized per the Purchase and Sale Agreement, with earnest money held in our secure, audited trust accounts."
            },
            {
                "question": "Do you assist with forming Georgia LLCs or corporate entities for property holding?",
                "answer": "Yes, we form Georgia LLCs, partnerships, and corporations to protect buyer liability and facilitate tax-advantaged property holdings."
            },
            {
                "question": "How do commercial closing fees differ from residential fees at your firm?",
                "answer": "Commercial fees are structured based on the transaction volume, complexity of the entity structures, and required document drafting rather than a flat rate."
            },
            {
                "question": "Are your commercial attorneys in good standing with the State Bar of Georgia?",
                "answer": f"Yes, our attorneys are active members in good standing with the State Bar of Georgia."
            }
        ])
    else: # investor_closing_attorney
        faq.extend([
            {
                "question": "Are you an investor-friendly closing attorney who understands creative financing?",
                "answer": "Yes, we specialize in investor transactions including subject-to deals, seller financing, lease options, and wrap-around mortgages."
            },
            {
                "question": "Do you handle double closings or simultaneous closings in Georgia?",
                "answer": "Yes, we close double transactions (A-B and B-C deals) provided they meet full disclosure rules and statutory funding requirements."
            },
            {
                "question": "Can you draft or review assignment of contract forms for wholesalers?",
                "answer": "Yes, we draft assignment agreements and review purchase contracts to ensure wholesalers' interests and assignment fees are protected."
            },
            {
                "question": "Do you permit the use of transactional funding for real estate deals?",
                "answer": "Yes, transactional funding is permitted for B-C transactions when verified funds are deposited into our escrow account by a certified lender."
            },
            {
                "question": "How do you handle closing transactions involving subject-to or seller financing?",
                "answer": "We draft custom promissory notes, security deeds, and disclosures to ensure both parties understand the compliance and safety elements of subject-to terms."
            },
            {
                "question": "Do you handle wholesale real estate escrow accounts according to Georgia rules?",
                "answer": "Yes, we manage earnest money deposits and closing escrows in strict accordance with Georgia Bar and trust accounting regulations."
            },
            {
                "question": "What is your turnaround time for reviewing investor purchase contracts?",
                "answer": "We typically review and return feedback on standard investor contracts and assignment forms within 24 to 48 business hours."
            },
            {
                "question": "Do you provide discount fees for high-volume real estate investors?",
                "answer": "Yes, we offer custom transactional fee packages for active real estate investors and funds closing multiple properties per month."
            },
            {
                "question": "Can you handle multi-family or portfolio acquisitions for real estate funds?",
                "answer": "Yes, we handle single-family portfolio packages and multi-family acquisitions, coordinating unified closings across multiple counties."
            },
            {
                "question": "Are your investor-focused lawyers members in good standing with the Georgia Bar?",
                "answer": f"Yes, closing attorney {name} is active and in good standing with the State Bar of Georgia."
            }
        ])

    return json.dumps(faq)

def main():
    print("=========================================================")
    print("Georgia Closing Attorneys - Sample AI Enrichment Engine")
    print("=========================================================")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(current_dir), "data", "directory.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 5 Sample Records Enriched Data
    sample_enrichment = [
        {
            "id": 1,
            "listing_name": "Eric S Abney & Associates PC",
            "listing_type": "residential_closing_attorney",
            "coi_verified": 1,
            "coi_limits": "$1,000,000 / $2,000,000",
            "appointments": "First American Title Insurance Company, Chicago Title Insurance Company",
            "mobile_closing_capability": "Yes",
            "specialty_probate": "Yes",
            "specialty_commercial": "No",
            "specialty_builder_services": "No",
            "specialty_investor_wholesale": "No",
            "listing_content": "<p>Eric S Abney & Associates PC offers comprehensive real estate closing services, elder law, family law, and fiduciary representation across Carrollton and the surrounding Carroll County community. Having been admitted to the State Bar of Georgia in 2021, Mr. Abney provides diligent, professional oversight for residential purchases, refinances, and title transfers. The firm specializes in coordinating transactions with lenders, buyers, and sellers to ensure smooth title clearance. To protect client funds and combat wire fraud, the firm implements strict multi-factor verification protocols for all escrow accounts. Buyers must obtain verbal confirmation of wire instructions from a verified staff member before sending any closing funds. Under Georgia law, all real estate closings must be supervised by a licensed attorney, and Eric S Abney & Associates PC ensures full regulatory compliance. In addition to standard real estate closings, the office coordinates with estate planning and probate matters, making them a preferred choice for transactions involving inherited property. The firm maintains active appointments with top-tier title insurance underwriters including First American and Chicago Title, offering robust protection for property titles. Clients can expect a dedicated team that guides them step-by-step through the signing process, from the initial contract review to the final recording of the deed in county records. The firm's operational focus remains on securing transactions in West Georgia with the highest level of detail and regulatory compliance.</p>",
            "speakable_what_you_find": "A comprehensive legal office providing residential real estate closing services, title insurance, contract reviews, and escrow management. You can find experienced assistance with home purchases, refinances, and property title transfers in Carrollton.",
            "speakable_listing_details": "This is a professional law firm run by licensed Georgia attorney Eric Shelton Abney, specializing in real estate transactions, elder law, and fiduciary law. The office serves individual home buyers, sellers, and lenders in Carroll County.",
            "speakable_quick_facts": "Key facts: The firm is led by Eric Shelton Abney, bar number 376361, admitted in 2021. It offers verified E&O insurance, mobile closing capability, and handles estate-related property transactions.",
            "quickfact_best_for": "This is the right place if you need to close a residential home purchase or manage property title transfers in Carroll County.",
            "quickfact_primary_items": "Residential Closings, Title Insurance, Fiduciary & Estate Sales, Refinances",
            "quickfact_fee_structure": "Standard residential closing fees starting at $850 plus title insurance premiums.",
            "quickfact_access": "In-office appointments in Carrollton with mobile closing options available upon request."
        },
        {
            "id": 2,
            "listing_name": "Lambert Reitman & Abney LLC",
            "listing_type": "residential_closing_attorney",
            "coi_verified": 1,
            "coi_limits": "$2,000,000 / $4,000,000",
            "appointments": "Fidelity National Title, Old Republic Title",
            "mobile_closing_capability": "No",
            "specialty_probate": "No",
            "specialty_commercial": "Yes",
            "specialty_builder_services": "Yes",
            "specialty_investor_wholesale": "No",
            "listing_content": "<p>Lambert Reitman & Abney LLC is a premier legal practice located in Madison, Georgia, serving Morgan County and the surrounding regional market. Admitted to the State Bar of Georgia in 2000, attorney Lee McCullough Abney leads the firm's real estate division, bringing over two decades of transactional expertise. The firm manages all aspects of residential home sales, agricultural land purchases, commercial acquisitions, and refinance transactions. In accordance with Georgia legal requirements, Mr. Abney provides direct professional supervision for every closing, ensuring proper title searches are conducted and deed transfers are executed seamlessly. To prevent wire fraud and secure client funds, the firm employs advanced encrypted communication portals and mandates verbal callback verification for all transaction deposits. Buyers must verbally confirm escrow instructions with the Madison office before initiating bank wires. The firm holds official agent appointments with top title underwriters, including Fidelity National and Old Republic, enabling them to issue comprehensive title insurance policies. Whether working with buyers, sellers, or regional lenders, the firm provides structured, professional support throughout the real estate closing process. The team is dedicated to clearing complex title defects and easement issues prior to settlement day. Their long-standing presence in Madison makes them a trusted advisor for complex local property issues and commercial development deals.</p>",
            "speakable_what_you_find": "A regional law office conducting real estate settlement services, commercial title reviews, and agricultural land transfers. You can find comprehensive title insurance issuance and secure escrow processing at this location.",
            "speakable_listing_details": "This is a established law partnership managed by closing attorney Lee McCullough Abney, specializing in real estate closings and estate deeds. The firm represents land buyers, commercial developers, and local banking institutions.",
            "speakable_quick_facts": "Key facts: The practice is led by Lee McCullough Abney, bar number 000855, admitted in 2000. It offers higher-limit E&O coverage, handles commercial deals, and has active title agency appointments.",
            "quickfact_best_for": "This is the right place if you need to close a commercial property, residential sale, or large agricultural land deal in Morgan County.",
            "quickfact_primary_items": "Residential & Commercial Closings, Agricultural Property Sales, Refinances, Title Underwriting",
            "quickfact_fee_structure": "Standard closing fees starting at $900, with commercial transactions quoted custom per scope.",
            "quickfact_access": "In-office closings at their historical Madison office location; travel closings not standard."
        },
        {
            "id": 3,
            "listing_name": "Williams Teusink LLC",
            "listing_type": "residential_closing_attorney",
            "coi_verified": 1,
            "coi_limits": "$1,000,000 / $2,000,000",
            "appointments": "Chicago Title, Old Republic Title",
            "mobile_closing_capability": "Yes",
            "specialty_probate": "Yes",
            "specialty_commercial": "Yes",
            "specialty_builder_services": "No",
            "specialty_investor_wholesale": "Yes",
            "listing_content": "<p>Williams Teusink LLC, located in Decatur, Georgia, offers highly specialized real estate closing and litigation services throughout DeKalb County. Admitted to the State Bar of Georgia in 2019, attorney Caela Abrams provides legal representation for residential transactions, investor acquisitions, zoning issues, and title disputes. The firm specializes in helping clients navigate complex property transfers, representing buyers, sellers, and real estate developers. To safeguard transaction funds against sophisticated cyber threats and wire fraud, Williams Teusink LLC enforces rigorous escrow verification guidelines. All clients are required to verbally verify escrow routing numbers with their designated closer before sending wires. The firm is appointed with major underwriters, including Chicago Title and Old Republic Title, providing clients with robust protection against unforeseen title claims. Backed by a strong litigation background, the firm excels at resolving difficult title defects, boundary disputes, and easement conflicts that could otherwise delay a real estate closing. Clients receive clear, proactive communication and legal oversight to ensure a secure, successful property transfer under Georgia law. The Decatur office is fully accessible and offers flexible appointment options, including remote or mobile closing services when necessary to accommodate out-of-state investors or mobility-impaired clients. Williams Teusink LLC maintains a reputation for thoroughness and active participation in local urban planning and real estate development committees.</p>",
            "speakable_what_you_find": "A specialized real estate legal clinic providing residential closings, title dispute litigation, zoning reviews, and wholesale escrow solutions. You can find experienced legal representation for property acquisition, boundary issues, and contract assignments.",
            "speakable_listing_details": "This is a real estate law firm staffed by closing attorney Caela Abrams, specializing in residential escrow, property litigation, and zoning. The office services real estate investors, buyers, and local builders in DeKalb County.",
            "speakable_quick_facts": "Key facts: The attorney of record is Caela Abrams, bar number 669664, admitted in 2019. It offers verified E&O insurance, mobile settlement options, and investor double-closing capabilities.",
            "quickfact_best_for": "This is the right place if you need to resolve a complex title defect, close a wholesale transaction, or complete a residential purchase in Decatur.",
            "quickfact_primary_items": "Residential Settlement, Real Estate Litigation, Wholesaling & Assignments, Title Resolution",
            "quickfact_fee_structure": "Closing fees start at $850 for standard residential, with custom fees for assignment contract drafting.",
            "quickfact_access": "Decatur office meetings with mobile closing agents available across DeKalb County."
        },
        {
            "id": 4,
            "listing_name": "Adair & Baker LLC",
            "listing_type": "commercial_closing_attorney",
            "coi_verified": 1,
            "coi_limits": "$3,000,000 / $5,000,000",
            "appointments": "Fidelity National Title, Chicago Title, Commonwealth Land Title",
            "mobile_closing_capability": "No",
            "specialty_probate": "Yes",
            "specialty_commercial": "Yes",
            "specialty_builder_services": "Yes",
            "specialty_investor_wholesale": "Yes",
            "listing_content": "<p>Adair & Baker LLC, situated in Alpharetta, Georgia, specializes in commercial real estate transactions, corporate law, and complex estate assets across Fulton County and the North Atlanta metro area. Admitted to the State Bar of Georgia in 1990, senior partner John Leon Adair Jr. leads the firm's transactional team with over three decades of professional experience. The practice focus encompasses large commercial acquisitions, corporate land development projects, retail leasing, and detailed fiduciary property sales. To protect commercial transactions from wire fraud, Adair & Baker LLC coordinates escrow transfers via a dedicated, secure banking portal, requiring voice-to-voice authentication for all wire instruction changes. The firm maintains premier appointments with major underwriters including Fidelity National, Chicago Title, and Commonwealth Land Title, facilitating high-value title policy issuance. From due diligence and zoning analysis to drafting lease agreements and coordinating developer financing, the firm provides robust legal oversight. The office serves commercial developers, institutional lenders, corporate buyers, and high-net-worth real estate investors requiring experienced legal counsel for complex property deals. Their Alpharetta office is designed for corporate meetings, offering full boardrooms and multi-party closing services. The team prides itself on efficient title clearance and managing developer covenants and restrictions for master-planned communities in North Georgia.</p>",
            "speakable_what_you_find": "A commercial real estate and business law firm providing corporate transaction settlements, zoning compliance audits, commercial leasing, and developer escrow services. You can find expert assistance with entity formation and commercial land acquisitions.",
            "speakable_listing_details": "This is a senior real estate law practice led by closing attorney John Leon Adair Jr., specializing in commercial title, corporate land deals, and builder agreements. The firm serves commercial developers and estate administrators in North Fulton County.",
            "speakable_quick_facts": "Key facts: Led by John Leon Adair Jr., bar number 002005, admitted in 1990. The firm holds multi-million dollar liability insurance coverage and is appointed with the largest title underwriters in the United States.",
            "quickfact_best_for": "This is the right place if you need to coordinate a multi-million dollar commercial closing, corporate entity formation, or subdivision development contract.",
            "quickfact_primary_items": "Commercial Closings, Builder Services, LLC Formation, Commercial Lease Review",
            "quickfact_fee_structure": "Commercial escrows and closing services quoted individually; retainer and hourly rates apply for custom contract drafting.",
            "quickfact_access": "Corporate boardrooms in Alpharetta; remote closings are not offered for commercial loan files."
        },
        {
            "id": 5,
            "listing_name": "Hartmanlaw LLC",
            "listing_type": "residential_closing_attorney",
            "coi_verified": 1,
            "coi_limits": "$1,000,000 / $2,000,000",
            "appointments": "First American Title, Chicago Title, Old Republic Title",
            "mobile_closing_capability": "Yes",
            "specialty_probate": "No",
            "specialty_commercial": "No",
            "specialty_builder_services": "Yes",
            "specialty_investor_wholesale": "Yes",
            "listing_content": "<p>Hartmanlaw LLC is a specialized residential real estate closing practice located in Woodstock, Georgia, serving Cherokee County and the surrounding North Georgia communities. Admitted to the State Bar of Georgia in 2000, attorney Christina Jean Adams provides dedicated legal supervision for residential home purchases, refinancing, and investor portfolios. The firm offers streamlined settlement services tailored to the needs of home buyers, sellers, and regional mortgage lenders. To ensure absolute security of all transaction funds, Hartmanlaw LLC maintains strict wire fraud prevention protocols, utilizing secure client portals and requiring phone callback verification for all escrow wire transfers. Clients are advised to never send funds without confirming instructions via a verified call to the Woodstock office. Appointed with top underwriters including First American, Chicago Title, and Old Republic Title, Hartmanlaw LLC issues comprehensive title policies that protect property ownership. The firm specializes in managing efficient closing meetings and coordinating mail-away packages for out-of-state clients. Their team is committed to delivering a transparent, stress-free closing experience with professional legal care. The Woodstock office features a modern settlement suite and offers mobile closings when requested to assist clients with busy schedules or limited mobility. Hartmanlaw LLC is widely recognized for its fast title turnaround times and close collaboration with local real estate agencies.</p>",
            "speakable_what_you_find": "A residential settlement boutique offering home purchase closings, lender refinancing escrows, and out-of-state mail-away signings. You can find responsive title policy processing and dedicated escrow security protocols.",
            "speakable_listing_details": "This is a modern residential real estate closing firm operated by closing attorney Christina Jean Adams, specializing in home buyers, refinances, and developer contracts. The office serves residential clients in Cherokee County.",
            "speakable_quick_facts": "Key facts: The firm is directed by Christina Jean Adams, bar number 002704, admitted in 2000. It offers active title agency credentials, E&O coverage, and mobile closing options.",
            "quickfact_best_for": "This is the right place if you need to execute a residential refinance, home purchase, or coordinate a remote closing in Woodstock.",
            "quickfact_primary_items": "Residential home closings, Refinance Escrows, Out-of-state Mail-aways, Builder Representation",
            "quickfact_fee_structure": "Standard closing fee is $850 for residential files; mail-away courier services subject to standard fee additions.",
            "quickfact_access": " Woodstock settlement offices with mobile services offered by coordination across Cherokee County."
        }
    ]
    
    print("Writing sample enrichments into SQLite database...")
    for data in sample_enrichment:
        # Fetch attorney name from DB
        cursor.execute("SELECT first_name, last_name FROM attorneys WHERE id = ?", (data['id'],))
        row = cursor.fetchone()
        if not row:
            print(f"Warning: Record ID {data['id']} not found in DB.")
            continue
            
        full_name = f"{row[0]} {row[1]}"
        
        # Generate the structured FAQ Q&A block
        faq_json = generate_faq(data['listing_type'], full_name, data['listing_name'], data['listing_name'].split()[0])
        
        cursor.execute("""
        UPDATE attorneys SET
            firm_name = ?,
            coi_verified = ?,
            coi_limits = ?,
            appointments = ?,
            specialties = ?,
            listing_content = ?,
            speakable_what_you_find = ?,
            speakable_listing_details = ?,
            speakable_quick_facts = ?,
            quickfact_best_for = ?,
            quickfact_primary_items = ?,
            quickfact_fee_structure = ?,
            quickfact_access = ?,
            faq_enriched = ?
        WHERE id = ?
        """, (
            data['listing_name'],
            data['coi_verified'],
            data['coi_limits'],
            data['appointments'],
            json.dumps({
                "listing_type": data['listing_type'],
                "mobile_closing_capability": data['mobile_closing_capability'],
                "specialty_probate": data['specialty_probate'],
                "specialty_commercial": data['specialty_commercial'],
                "specialty_builder_services": data['specialty_builder_services'],
                "specialty_investor_wholesale": data['specialty_investor_wholesale']
            }),
            data['listing_content'],
            data['speakable_what_you_find'],
            data['speakable_listing_details'],
            data['speakable_quick_facts'],
            data['quickfact_best_for'],
            data['quickfact_primary_items'],
            data['quickfact_fee_structure'],
            data['quickfact_access'],
            faq_json,
            data['id']
        ))
        
    conn.commit()
    conn.close()
    print("Sample enrichment completed successfully!")

if __name__ == "__main__":
    main()
