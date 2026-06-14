import os

# Define the counties
counties = {
    "macon-bibb": {
        "db_name": "Bibb",
        "title_county": "Macon-Bibb County",
        "cities": "Macon",
        "title": "Macon-Bibb County Grease Trap Pumping Directory",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Macon-Bibb County, GA. Find contractors in Macon.",
        "header": "Macon-Bibb Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Macon and Bibb County, Georgia.",
        "faq_1_q": "What are the grease trap rules in Macon, GA?",
        "faq_1_a": "Macon Water Authority requires commercial kitchens to pump grease interceptors when the combined grease and food solids depth exceeds 25% of the liquid capacity, or at least once every quarter (90 days).",
        "faq_2_q": "How do I check if a grease hauler is licensed in Bibb County?",
        "faq_2_a": "All grease trap hauling vehicles must display an active Macon-Bibb County Board of Health waste transport permit and maintain EPD FOG registrations."
    },
    "houston": {
        "db_name": "Houston",
        "title_county": "Houston County",
        "cities": "Warner Robins, Perry",
        "title": "Houston County Grease Trap Pumping Directory | Warner Robins & Perry",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Houston County, GA. Find contractors in Warner Robins and Perry.",
        "header": "Houston County Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Warner Robins, Perry, and Houston County, Georgia.",
        "faq_1_q": "What are the grease trap pumping requirements in Houston County?",
        "faq_1_a": "Houston County Environmental Health and city codes in Warner Robins and Perry require regular grease trap maintenance and manifest records to prevent sewer line blockages.",
        "faq_2_q": "How do I find permitted grease haulers in Warner Robins or Perry?",
        "faq_2_a": "You can use our verified directory of FOG-permitted grease trap service companies serving Houston County, Georgia, to hire licensed contractors."
    },
    "peach": {
        "db_name": "Peach",
        "title_county": "Peach County",
        "cities": "Fort Valley, Byron",
        "title": "Peach County Grease Trap Pumping Directory | Fort Valley & Byron",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Peach County, GA. Find contractors in Fort Valley and Byron.",
        "header": "Peach County Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Fort Valley, Byron, and Peach County, Georgia.",
        "faq_1_q": "What are the grease trap rules in Byron and Fort Valley?",
        "faq_1_a": "Peach County municipal codes mandate commercial kitchens to clean and pump grease interceptors regularly to keep wastewater discharges compliant with local standards.",
        "faq_2_q": "How do I verify a grease hauler in Peach County?",
        "faq_2_a": "Ensure the contractor holds a valid Georgia EPD commercial waste transporter registration and is listed in the Southeastern FOG Alliance database."
    },
    "jones": {
        "db_name": "Jones",
        "title_county": "Jones County",
        "cities": "Gray",
        "title": "Jones County Grease Trap Pumping Directory | Gray, GA",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Jones County, GA. Find contractors in Gray.",
        "header": "Jones County Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Gray and Jones County, Georgia.",
        "faq_1_q": "What grease trap rules apply to businesses in Gray, GA?",
        "faq_1_a": "Commercial businesses in Jones County must pump grease interceptors regularly to prevent fat and oil accumulation from disrupting the municipal sewer system.",
        "faq_2_q": "Who is a local grease trap cleaning contractor in Jones County?",
        "faq_2_a": "Marlers Plumbing Services, LLC is physically located in Gray (Jones County) and is fully permitted under FOG478 to clean commercial interceptors."
    },
    "monroe": {
        "db_name": "Monroe",
        "title_county": "Monroe County",
        "cities": "Forsyth",
        "title": "Monroe County Grease Trap Pumping Directory | Forsyth, GA",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Monroe County, GA. Find contractors in Forsyth.",
        "header": "Monroe County Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Forsyth and Monroe County, Georgia.",
        "faq_1_q": "What are the grease trap requirements in Forsyth, GA?",
        "faq_1_a": "Monroe County health regulations require commercial food establishments to perform quarterly grease interceptor pumping to ensure sewer lines remain free of grease blockages.",
        "faq_2_q": "How do I find a certified grease hauler in Monroe County?",
        "faq_2_a": "Verify the transporter is registered under the Georgia EPD commercial transporter program and carries verified waste manifests."
    },
    "baldwin": {
        "db_name": "Baldwin",
        "title_county": "Baldwin County",
        "cities": "Milledgeville",
        "title": "Baldwin County Grease Trap Pumping Directory | Milledgeville, GA",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Baldwin County, GA. Find contractors in Milledgeville.",
        "header": "Baldwin County Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Milledgeville and Baldwin County, Georgia.",
        "faq_1_q": "What are the grease trap rules in Milledgeville, GA?",
        "faq_1_a": "The City of Milledgeville and Baldwin County require regular grease interceptor cleaning and manifest logging to comply with sewer system maintenance codes.",
        "faq_2_q": "Who can pump commercial grease interceptors in Milledgeville?",
        "faq_2_a": "Any contractor listed in our registry that serves Baldwin County and holds an active Georgia EPD transporter registration is permitted to perform service."
    },
    "laurens": {
        "db_name": "Laurens",
        "title_county": "Laurens County",
        "cities": "Dublin",
        "title": "Laurens County Grease Trap Pumping Directory | Dublin, GA",
        "desc": "Verify licensed grease trap pumpers and compliance transporters servicing Laurens County, GA. Find contractors in Dublin and East Dublin.",
        "header": "Laurens County Grease Trap Directory",
        "lead": "Verify licensed liquid waste haulers, check local compliance credentials, and run the FOG calculator. Serving commercial kitchens and foodservice establishments in Dublin, East Dublin, and Laurens County, Georgia.",
        "faq_1_q": "What are the grease trap cleaning guidelines in Dublin, GA?",
        "faq_1_a": "Dublin utilities require all food establishments to clean grease interceptors regularly and keep disposal manifests to trace all hauled commercial liquid waste.",
        "faq_2_q": "Who is a local grease trap cleaning contractor in Laurens County?",
        "faq_2_a": "AmeriPro Environmental Services is located in Dublin (Laurens County) and is permitted under FOG500 to perform commercial grease trap maintenance."
    }
}

template = """---
import Layout from '../layouts/Layout.astro';
import Calculator from '../components/Calculator.astro';
import ListingCard from '../components/ListingCard.astro';
import { getHaulersByCounty } from '../data/db.js';

const haulers = getHaulersByCounty('__DB_NAME__');

// Compile schemas: CollectionPage + ItemList + FAQPage
const hubSchema = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "CollectionPage",
      "@id": "https://macongreasetrap.com/__SLUG__#webpage",
      "url": "https://macongreasetrap.com/__SLUG__",
      "name": "__TITLE__",
      "description": "__DESC__",
      "speakable": {
        "@type": "SpeakableSpecification",
        "cssSelector": [".speakable-header", ".speakable-intro"]
      }
    },
    {
      "@type": "ItemList",
      "@id": "https://macongreasetrap.com/__SLUG__#itemlist",
      "name": "__TITLE_COUNTY__ Licensed Liquid Waste Contractors Registry",
      "description": "Comprehensive index of permitted grease haulers servicing __TITLE_COUNTY__, GA.",
      "itemListElement": haulers.map((h, i) => ({
        "@type": "ListItem",
        "position": i + 1,
        "url": `https://macongreasetrap.com/${h.slug}`
      }))
    },
    {
      "@type": "FAQPage",
      "@id": "https://macongreasetrap.com/__SLUG__#faqpage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "__FAQ_1_Q__",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "__FAQ_1_A__"
          }
        },
        {
          "@type": "Question",
          "name": "__FAQ_2_Q__",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "__FAQ_2_A__"
          }
        }
      ]
    }
  ]
};
---

<Layout 
  title="__TITLE__" 
  description="__DESC__"
  schema={hubSchema}
>
  <div class="hub-container">
    
    <!-- Breadcrumbs -->
    <div class="breadcrumbs">
      <a href="/">Home</a> <span class="sep">➔</span> <a href="/georgia">Georgia</a> <span class="sep">➔</span> <span class="current">__TITLE_COUNTY__</span>
    </div>

    <!-- Above the Fold: Hero Section with Reciprocity Calculator -->
    <section class="hero-split">
      <div class="hero-text">
        <h1 class="speakable-header">__HEADER__</h1>
        <p class="lead speakable-intro">
          __LEAD__
        </p>
        
        <div class="quick-links">
          <a href="#listings" class="btn btn-primary">Browse {haulers.length} Contractors</a>
          <a href="/macon-grease-trap-requirements" class="btn btn-secondary">Read MWA Rules</a>
        </div>
      </div>
      
      <div class="hero-calculator">
        <Calculator />
      </div>
    </section>

    <!-- Listings & Filters Grid Section -->
    <section id="listings" class="listings-section">
      <h2 class="section-title">Verified Grease Pumping & Disposal Contractors</h2>
      <p class="section-subtitle">Use the filters below to find grease trap haulers operating in __TITLE_COUNTY__.</p>
      
      <!-- Interactive Filter Bar -->
      <div class="filter-bar card">
        <div class="filter-info">
          <span>Showing <strong>{haulers.length}</strong> Registered Contractors</span>
        </div>
        <div class="filter-badges">
          <button class="filter-tag active" data-type="all" aria-label="Show all services">All Services</button>
        </div>
      </div>

      <!-- Listings Grid -->
      <div class="listings-grid grid-cols-3" style="margin-top: 2rem;">
        {haulers.map(hauler => (
          <div 
            class="listing-wrapper" 
            data-grease="1" 
          >
            <ListingCard hauler={hauler} />
          </div>
        ))}
      </div>
    </section>

    <!-- Adjacent County Silo Interlinking Section -->
    <section class="adjacent-counties card">
      <h3>Regional Middle Georgia Coverage</h3>
      <p>
        Looking for grease trap pumping in other Middle Georgia counties? Check our active regional directories:
      </p>
      <div class="counties-grid">
__COUNTIES_LINKS__
      </div>
    </section>

  </div>
</Layout>

<style>
  .hub-container {
    padding: 1.5rem 0;
  }

  .breadcrumbs {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
  }

  .breadcrumbs a:hover {
    color: var(--accent-emerald);
  }

  .breadcrumbs .sep {
    margin: 0 0.5rem;
    font-size: 0.75rem;
  }

  .breadcrumbs .current {
    color: var(--text-primary);
    font-weight: 500;
  }

  .hero-split {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 3rem;
    align-items: center;
    padding: 2rem 0 4rem;
  }

  .hero-text h1 {
    font-size: 2.8rem;
    line-height: 1.15;
    margin-bottom: 1.25rem;
    background: linear-gradient(135deg, var(--text-primary) 30%, var(--text-secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .lead {
    font-size: 1.1rem;
    color: var(--text-secondary);
    line-height: 1.7;
    margin-bottom: 2rem;
  }

  .quick-links {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .listings-section {
    margin-top: 2rem;
    margin-bottom: 4rem;
  }

  .section-title {
    font-size: 1.8rem;
    text-align: center;
    color: var(--text-primary);
  }

  .section-subtitle {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.95rem;
    max-width: 600px;
    margin: 0.5rem auto 1.5rem;
  }

  .filter-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
  }

  .filter-info {
    font-size: 0.95rem;
  }

  .filter-badges {
    display: flex;
    gap: 0.75rem;
  }

  .filter-tag {
    background-color: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 0.4rem 1rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    font-family: inherit;
    margin: 0;
    transition: var(--transition-smooth);
  }

  .filter-tag:hover {
    border-color: var(--accent-emerald);
    color: var(--text-primary);
  }

  .filter-tag.active {
    background-color: var(--accent-emerald-muted);
    border-color: var(--accent-emerald);
    color: var(--accent-emerald);
  }

  .adjacent-counties {
    background: hsla(218, 28%, 15%, 0.4);
    padding: 2rem;
    margin-bottom: 2rem;
  }

  .adjacent-counties h3 {
    font-size: 1.4rem;
    margin-bottom: 0.5rem;
  }

  .adjacent-counties p {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
  }

  .counties-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1.25rem;
  }

  .county-link-box {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    transition: var(--transition-smooth);
    text-decoration: none;
  }

  .county-link-box:hover {
    border-color: var(--accent-emerald);
    transform: translateY(-2px);
  }

  .county-link-box strong {
    font-size: 0.95rem;
    color: var(--text-primary);
  }

  .county-link-box span {
    font-size: 0.8rem;
    color: var(--text-muted);
  }

  @media (max-width: 992px) {
    .hero-split {
      grid-template-columns: 1fr;
      gap: 2.5rem;
      text-align: center;
    }
    .hero-text h1 {
      font-size: 2.3rem;
    }
    .quick-links {
      justify-content: center;
    }
    .filter-bar {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }
  }
</style>

<script is:inline>
  // Fast, client-side filtering logic
  (function() {
    const tags = document.querySelectorAll('.filter-tag');
    const items = document.querySelectorAll('.listing-wrapper');

    tags.forEach(tag => {
      tag.addEventListener('click', () => {
        tags.forEach(t => t.classList.remove('active'));
        tag.classList.add('active');
      });
    });
  })();
</script>
"""

pages_dir = r"C:\Users\tamo4\git\bigfoot-sites\macongreasetrap.com\src\pages"

for slug, data in counties.items():
    # Build counties links
    links_html = []
    for other_slug, other_data in counties.items():
        if other_slug == slug:
            continue
        links_html.append(f"""        <a href="/{other_slug}" class="county-link-box">
          <strong>{other_data["title_county"]}</strong>
          <span>{other_data["cities"]}</span>
          <span class="badge badge-verified" style="background-color: var(--accent-emerald-muted); color: var(--accent-emerald); padding: 0.1rem 0.4rem; border-radius: var(--radius-sm); font-size: 0.7rem; align-self: flex-start; margin-top: 0.25rem;">Active Hub</span>
        </a>""")
        
    counties_links = "\n".join(links_html)
    
    file_content = template
    file_content = file_content.replace('__DB_NAME__', data["db_name"])
    file_content = file_content.replace('__SLUG__', slug)
    file_content = file_content.replace('__TITLE__', data["title"])
    file_content = file_content.replace('__DESC__', data["desc"])
    file_content = file_content.replace('__TITLE_COUNTY__', data["title_county"])
    file_content = file_content.replace('__HEADER__', data["header"])
    file_content = file_content.replace('__LEAD__', data["lead"])
    file_content = file_content.replace('__FAQ_1_Q__', data["faq_1_q"])
    file_content = file_content.replace('__FAQ_1_A__', data["faq_1_a"])
    file_content = file_content.replace('__FAQ_2_Q__', data["faq_2_q"])
    file_content = file_content.replace('__FAQ_2_A__', data["faq_2_a"])
    file_content = file_content.replace('__COUNTIES_LINKS__', counties_links)
    
    file_path = os.path.join(pages_dir, f"{slug}.astro")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"Generated page: {file_path}")

print("County page generation complete!")
