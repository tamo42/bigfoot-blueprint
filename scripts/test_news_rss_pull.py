import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timedelta
import time

try:
    import trafilatura
    from googlenewsdecoder import new_decoderv1
except ImportError:
    print("Please install trafilatura and googlenewsdecoder")
    exit(1)

# Define our niches and their targeted queries
NICHES = {
    "Closing Attorneys": [
        '"real estate" AND ("closing" OR "escrow" OR "title insurance")',
        '"Georgia" AND ("real estate law" OR "property tax")',
        '"mortgage rates" AND "housing market"'
    ],
    "Grease Trap Cleaning": [
        '"grease trap" AND ("cleaning" OR "pumping" OR "maintenance")',
        '"FOG" AND ("fats oils grease" OR "wastewater" OR "sewer")',
        '"restaurant" AND ("health inspection" OR "compliance" OR "fines") AND "grease"'
    ]
}

def parse_pubdate(date_str):
    """Parse RSS pubDate to datetime object. Example: Fri, 12 Jun 2026 18:00:00 GMT"""
    try:
        # standard RSS date format
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
    except ValueError:
        try:
            # Sometimes it might be slightly different
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            return datetime.utcnow() # fallback to now if we can't parse

def fetch_article_text(url):
    """Attempt to fetch and extract the main text of the article."""
    try:
        # Decode the Google News URL first
        decoded_response = new_decoderv1(url)
        if decoded_response.get("status"):
            real_url = decoded_response.get("decoded_url")
            print(f"      -> Decoded URL: {real_url}")
        else:
            print("      [!] Failed to decode URL, falling back to original.")
            real_url = url
            
        # trafilatura.fetch_url handles redirects and basic bot evasion automatically
        downloaded = trafilatura.fetch_url(real_url)
        if downloaded is None:
            return None
            
        # extract the text
        result = trafilatura.extract(downloaded)
        return result
    except Exception as e:
        print(f"      [!] Error extracting text from {url}: {e}")
        return None

def fetch_google_news(query, last_24_hours_only=True):
    # To enforce 24h on Google News RSS, we can add ' when:1d' to the query
    time_modifier = " when:1d" if last_24_hours_only else ""
    encoded_query = urllib.parse.quote(query + time_modifier)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            items = []
            now = datetime.utcnow()
            
            for item in root.findall('.//item'):
                pubDate_str = item.find('pubDate').text if item.find('pubDate') is not None else ''
                
                # Check date if we are doing manual date filtering
                if last_24_hours_only and pubDate_str:
                    pub_date = parse_pubdate(pubDate_str)
                    if now - pub_date > timedelta(hours=24):
                        continue # Skip older articles
                
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                source_elem = item.find('source')
                source = source_elem.text if source_elem is not None else ''
                
                print(f"    -> Found: {title[:60]}...")
                
                # Try to get the full text
                article_text = fetch_article_text(link)
                
                items.append({
                    "title": title,
                    "link": link,
                    "published": pubDate_str,
                    "source": source,
                    "full_text": article_text,
                    "text_extracted_successfully": article_text is not None
                })
                
                # Throttle slightly so we don't get banned while testing
                time.sleep(1)
                
                if len(items) >= 3: # Limit to top 3 for this test to save time
                    break
            return items
    except Exception as e:
        print(f"Error fetching query '{query}': {e}")
        return []

def main():
    results = {}
    
    print("Starting targeted news pull (Last 24 Hours Only) with Full Text Extraction...")
    for niche, queries in NICHES.items():
        print(f"\nProcessing Niche: {niche}")
        results[niche] = []
        
        for query in queries:
            print(f"  Fetching query: {query}")
            articles = fetch_google_news(query, last_24_hours_only=True)
            
            results[niche].append({
                "query": query,
                "article_count": len(articles),
                "articles": articles
            })
            
    cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    output_file = os.path.join(cache_dir, 'test_news_pull_results_full_text.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nSuccessfully saved results to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
