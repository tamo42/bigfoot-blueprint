import os
import re
import time
import random
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

TRACKER_PATH = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p2_states_tracker.md"
LOG_PATH = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\03-WELLS_Scout_Log.md"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

KEYWORDS = ['csv', 'excel', 'download', 'api', 'arcgis', 'soda', 'json', 'export', 'bulk', 'dataset']
API_DOC_KEYWORDS = ['swagger', 'openapi', 'authentication', 'api key', 'bearer', 'oauth']

def parse_tracker():
    states = []
    with open(TRACKER_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and ('Not Started' in line or 'In Progress' in line):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 6:
                    state_raw = parts[1].replace('**', '')
                    url_md = parts[6]
                    url_match = re.search(r'\[.*?\]\((.*?)\)', url_md)
                    if url_match:
                        url = url_match.group(1)
                        if not url.startswith('http'):
                            url = 'https://' + url
                        states.append((state_raw, url))
    return states

def check_url(url):
    try:
        time.sleep(random.uniform(1.5, 3.5))  # Human mimicry
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return "None", None, False
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text().lower()
        
        method = "None"
        found_url = None
        precision_bonus = False

        for a in soup.find_all('a', href=True):
            href = a['href']
            lower_href = href.lower()
            text_a = a.get_text().lower()
            
            if any(k in lower_href for k in KEYWORDS) or any(k in text_a for k in KEYWORDS):
                method = "Bulk/API"
                found_url = urljoin(url, href)
                break
                
        # Gamification: Precision Bonus Check
        if method == "Bulk/API" and any(k in text for k in API_DOC_KEYWORDS):
            precision_bonus = True

        return method, found_url, precision_bonus
    except Exception as e:
        return "None", None, False

def main():
    states = parse_tracker()
    
    # Read already processed states from log
    processed = set()
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            processed = set(re.findall(r'## State: (.+)', content))

    with open(LOG_PATH, 'a', encoding='utf-8') as log_f:
        for state, url in states:
            if state in processed:
                continue
            
            print(f"Scouting {state} at {url} ...")
            method, found_url, bonus = check_url(url)
            
            log_f.write(f"\n## State: {state}\n")
            if method == "Bulk/API":
                log_f.write(f"- **Method Found**: {method}\n")
                log_f.write(f"- **Source URL**: {found_url}\n")
                log_f.write(f"- **Local File Path**: N/A\n")
                if bonus:
                    log_f.write(f"- **Precision Bonus**: Awarded! (Machine-readable auth docs detected)\n")
            else:
                log_f.write(f"- **Method Found**: None\n")
                log_f.write(f"- **Source URL**: {url}\n")
                log_f.write(f"- **Local File Path**: N/A\n")
                log_f.write(f"- **Notes**: Pending_Manual_Review\n")
            
            log_f.flush()

if __name__ == '__main__':
    main()
