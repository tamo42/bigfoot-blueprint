import os
import re
import sys
import time
import json
import sqlite3
import argparse
import requests
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Set path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import p3_utils as utils

# HTTP configurations
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}
TIMEOUT = 8

def get_base_domain(url):
    """
    Extracts the base netloc domain (e.g., example.com) from a URL, stripping 'www.'.
    """
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc

def clean_html_to_text(html_content):
    """
    Parses HTML content, strips boilerplate elements (scripts, styles, navs, footers),
    and returns cleaned, compact text.
    """
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Strip boilerplate tags
    for element in soup(["script", "style", "nav", "footer", "header", "head", "noscript", "iframe", "svg", "aside", "form"]):
        element.decompose()
        
    # 1b. Strip boilerplate classes and IDs
    for element in soup.find_all(class_=re.compile(r'(?i)footer|sidebar|menu|nav|widget|popup|modal|banner|ads')):
        element.decompose()
    for element in soup.find_all(id=re.compile(r'(?i)footer|sidebar|menu|nav|widget|popup|modal|banner|ads')):
        element.decompose()
        
    # 2. Extract visible text
    text = soup.get_text(separator="\n")
    
    # 3. Clean up whitespace and consecutive blank lines
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = []
    for line in lines:
        if line:
            # Filter cookie banners, copyright footers
            if any(term in line.lower() for term in ("cookie", "privacy policy", "all rights reserved", "copyright ©")):
                continue
            clean_lines.append(line)
            
    return "\n".join(clean_lines)

def fetch_page(url):
    """
    Fetches HTML content of a URL with UA spoofing, timeouts, and SSL fallback.
    """
    # Normalize URL scheme
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=True)
        response.raise_for_status()
        return response.text, response.url
    except requests.exceptions.SSLError:
        # Retry once without SSL verification
        try:
            print(f"    [~] SSL error for {url}. Retrying without verification...")
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            response.raise_for_status()
            return response.text, response.url
        except Exception as e:
            return None, str(e)
    except Exception as e:
        return None, str(e)

def is_valid_crawl_link(url):
    """
    Filters out binary files, login portals, social media links, and other non-HTML endpoints.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    netloc = parsed.netloc.lower()
    
    # 1. Skip non-HTTP links
    if parsed.scheme not in ("http", "https"):
        return False
        
    # 2. Skip social media or external authority domains
    social_domains = [
        "facebook.com", "twitter.com", "instagram.com", "youtube.com", 
        "linkedin.com", "yelp.com", "pinterest.com", "google.com", "savannahchamber.com"
    ]
    if any(sd in netloc for sd in social_domains):
        return False
        
    # 3. Skip binary/non-HTML extensions
    binary_extensions = [
        ".zip", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4", 
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".exe", ".tar", 
        ".gz", ".xml", ".json", ".txt", ".csv", ".msi"
    ]
    if any(path.endswith(ext) for ext in binary_extensions):
        return False
        
    # 4. Skip admin/login/transactional and low-value content paths (blogs, tags, pagination, APIs, legal)
    skip_paths = [
        # Admin / Auth
        "wp-login", "wp-admin", "login", "admin", "checkout", "cart", "account", "signin", "signup", "config",
        # Feeds, Blogs & Pagination
        "/blog", "/news", "/category", "/tag", "/author", "/archive", "/page/", "comment", "/post/", "/feed/", "/rss/",
        # Legal / Boilerplate
        "privacy", "terms", "disclaimer", "cookie",
        # CMS / API / System
        "wp-json", "wp-content", "wp-includes", "xmlrpc", "trackback", "_api", "_serverless", "_next", "_nuxt", "cdn-cgi", "replytocom",
        # Low Value Content
        "/events/", "/calendar/", "/search", "/collections/", "/products/", "/gallery/", "/portfolio/"
    ]
    if any(sp in path for sp in skip_paths):
        return False
        
    # Also skip query string pagination like ?page=2 or ?p=123
    if "page=" in parsed.query.lower() or "p=" in parsed.query.lower():
        return False
        
    return True

def extract_internal_links(html, base_url):
    """
    Extracts internal links from HTML matching the same base domain,
    prioritizing pages containing services/about keywords.
    """
    soup = BeautifulSoup(html, 'html.parser')
    base_domain = get_base_domain(base_url)
    
    internal_links = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        
        # Check if same domain and valid link type
        if get_base_domain(full_url) == base_domain:
            # Strip anchors and parameters
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            if is_valid_crawl_link(clean_url):
                internal_links.add(clean_url)
            
    # Score links based on utility keywords
    scored_links = []
    keywords = ["service", "about", "capability", "drilling", "pump", "contact", "water", "filter", "inspect"]
    
    for link in internal_links:
        # Skip homepage links
        if urlparse(link).path in ("", "/"):
            continue
            
        score = 0
        path_lower = urlparse(link).path.lower()
        for kw in keywords:
            if kw in path_lower:
                score += 10
                
        # Prefer shorter paths (usually primary pages)
        score -= len(urlparse(link).path.split("/"))
        
        scored_links.append((link, score))
        
    # Sort by score descending
    scored_links.sort(key=lambda x: x[1], reverse=True)
    return [link for link, score in scored_links]

def crawl_contractor_site(website_url, output_path, failed_path):
    """
    Performs targeted crawling of a website (homepage + up to 4 prioritized interior pages),
    and applies cross-page line frequency filtering to strip repeated navigation/footers.
    """
    # Check if homepage itself is valid (e.g. not a facebook page or zip)
    if not is_valid_crawl_link(website_url):
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(f"Crawl Failed: Invalid website link type (e.g. social media or binary file). URL: {website_url}")
        print(f"  [-] Skipped invalid website type: {website_url}")
        return False

    print(f"[*] Crawling: {website_url}...")
    
    # 1. Fetch homepage
    html, resolved_url = fetch_page(website_url)
    if not html:
        # Save failure log
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(f"Crawl Failed: Homepage Unreachable.\nDetails: {resolved_url}")
        print(f"  [-] Homepage unreachable: {resolved_url}")
        return False
        
    homepage_text = clean_html_to_text(html)
    homepage_lines = [line.strip() for line in homepage_text.splitlines() if line.strip()]
    
    pages_content = [
        {
            "url": resolved_url,
            "lines": homepage_lines,
            "is_homepage": True
        }
    ]
    
    # 2. Find internal links
    internal_links = extract_internal_links(html, resolved_url)
    
    # Take top 4 prioritized internal links
    target_links = internal_links[:4]
    
    # 3. Crawl interior links
    for link in target_links:
        print(f"  [+] Crawling subpage: {link}...")
        sub_html, sub_err = fetch_page(link)
        if sub_html:
            sub_text = clean_html_to_text(sub_html)
            sub_lines = [line.strip() for line in sub_text.splitlines() if line.strip()]
            pages_content.append({
                "url": link,
                "lines": sub_lines,
                "is_homepage": False
            })
            time.sleep(0.5) # Politeness delay
        else:
            print(f"    [-] Failed to crawl subpage {link}: {sub_err}")
            
    # 4. Count line frequencies across all crawled pages of the site
    line_counts = {}
    for page in pages_content:
        # Deduplicate lines within the same page for frequency count
        for line in set(page["lines"]):
            line_counts[line] = line_counts.get(line, 0) + 1
            
    # 5. Apply filtering and compile outputs
    total_chars_raw = 0
    total_chars_cleaned = 0
    output_blocks = []
    
    for page in pages_content:
        raw_page_text = "\n".join(page["lines"])
        total_chars_raw += len(raw_page_text)
        
        if page["is_homepage"]:
            # Homepage retains all content to preserve baseline site structures/menus
            filtered_lines = page["lines"]
        else:
            # Subpages strip lines that appear on multiple pages AND are under 60 characters
            filtered_lines = []
            for line in page["lines"]:
                if line_counts.get(line, 0) > 1 and len(line) < 60:
                    continue
                filtered_lines.append(line)
                
        cleaned_page_text = "\n".join(filtered_lines)
        total_chars_cleaned += len(cleaned_page_text)
        
        header = f"=== HOMEPAGE ({page['url']}) ===" if page["is_homepage"] else f"=== SUBPAGE ({page['url']}) ==="
        output_blocks.append(f"{header}\n{cleaned_page_text}")
        
    full_text = "\n\n".join(output_blocks)
    
    # 6. Save combined filtered text to cache file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"  [+] Saved crawled content to: {output_path}")
    print(f"      - Raw characters: {total_chars_raw} | Cleaned characters: {total_chars_cleaned}")
    savings = ((total_chars_raw - total_chars_cleaned) / max(1, total_chars_raw)) * 100
    print(f"      - Token/Char savings: {savings:.1f}%")
    return True

class CrawlProgressTracker:
    """
    Thread-safe tracker to export crawler progress to a JSON status file.
    """
    def __init__(self, progress_path, total):
        self.progress_path = progress_path
        self.total = total
        self.success = 0
        self.fail = 0
        self.pending = total
        self.active_crawls = {}
        self.lock = threading.Lock()
        
    def start_crawl(self, url):
        with self.lock:
            self.active_crawls[url] = time.time()
            self._write()
            
    def end_crawl(self, url, success):
        with self.lock:
            if url in self.active_crawls:
                del self.active_crawls[url]
            if success:
                self.success += 1
            else:
                self.fail += 1
            self.pending = max(0, self.total - self.success - self.fail)
            self._write()
            
    def _write(self):
        try:
            data = {
                "total": self.total,
                "success": self.success,
                "fail": self.fail,
                "pending": self.pending,
                "active_crawls": [
                    {"url": url, "started_at": start_time}
                    for url, start_time in self.active_crawls.items()
                ]
            }
            with open(self.progress_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

def crawl_state_websites(db_path, state_name, limit, overwrite=False, max_workers=5):
    """
    Queries state database and crawls websites for records needing content.
    """
    state_to_folder = {
        "GA": "georgia",
        "MI": "michigan",
        "NY": "new_york",
        "NC": "north_carolina",
        "OH": "ohio",
        "PA": "pennsylvania",
        "TX": "texas",
        "VA": "virginia"
    }
    
    # Map state name to abbreviation if needed
    state_abbrev = None
    if state_name and state_name.lower() != 'all':
        state_map = {
            "georgia": "GA", "michigan": "MI", "new york": "NY", "new_york": "NY",
            "north carolina": "NC", "north_carolina": "NC", "ohio": "OH",
            "pennsylvania": "PA", "texas": "TX", "virginia": "VA",
            "ga": "GA", "mi": "MI", "ny": "NY", "nc": "NC", "oh": "OH",
            "pa": "PA", "tx": "TX", "va": "VA"
        }
        state_abbrev = state_map.get(state_name.lower(), state_name.upper())
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Select rows with a website
    if state_abbrev:
        c.execute("""
            SELECT id, slug, website_url, state
            FROM well_contractors 
            WHERE website_url IS NOT NULL 
              AND website_url != ''
              AND UPPER(state) = ?
        """, (state_abbrev,))
    else:
        c.execute("""
            SELECT id, slug, website_url, state
            FROM well_contractors 
            WHERE website_url IS NOT NULL 
              AND website_url != ''
        """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print(f"[+] No websites to crawl in database.")
        return
        
    # Filter pending rows based on cache existence and overwrite flag
    pending_rows = []
    for row in rows:
        row_id, slug, website_url, row_state = row
        state_folder = state_to_folder.get(row_state.upper() if row_state else "", "general")
        cache_dir = utils.resolve_path(f"cache/crawled_text/{state_folder}")
        os.makedirs(cache_dir, exist_ok=True)
        
        output_path = os.path.join(cache_dir, f"{slug}.txt")
        failed_path = os.path.join(cache_dir, f"{slug}.failed")
        
        if overwrite:
            # Delete existing files if overwriting
            if os.path.exists(output_path): os.remove(output_path)
            if os.path.exists(failed_path): os.remove(failed_path)
            pending_rows.append((row_id, slug, website_url, output_path, failed_path))
        else:
            if not os.path.exists(output_path) and not os.path.exists(failed_path):
                pending_rows.append((row_id, slug, website_url, output_path, failed_path))
            
    print(f"[*] Found {len(rows)} records with websites, {len(pending_rows)} are pending crawl.")
    
    # Apply limit
    pending_rows = pending_rows[:limit]
    if not pending_rows:
        print("[+] All pending websites have already been crawled/attempted in this state.")
        return
        
    # Setup progress file
    progress_path = utils.resolve_path("cache/crawl_progress.json")
    if os.path.exists(progress_path):
        try: os.remove(progress_path)
        except Exception: pass
        
    tracker = CrawlProgressTracker(progress_path, len(pending_rows))

    print(f"[*] Starting crawl run for {len(pending_rows)} sites in {state_name} with {max_workers} workers...")
    success_count = 0
    fail_count = 0
    
    # Disable warnings for insecure requests (verify=False retry)
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    
    def process_row(row):
        row_id, slug, website_url, output_path, failed_path = row
        if os.path.exists(output_path):
            tracker.end_crawl(website_url, success=True)
            return "cached_success"
        elif os.path.exists(failed_path):
            tracker.end_crawl(website_url, success=False)
            return "cached_fail"
            
        tracker.start_crawl(website_url)
        try:
            success = crawl_contractor_site(website_url, output_path, failed_path)
            tracker.end_crawl(website_url, success)
            return "success" if success else "fail"
        except Exception as e:
            print(f"  [-] Exception crawling {website_url}: {e}")
            try:
                with open(failed_path, "w", encoding="utf-8") as f:
                    f.write(f"Crawl Failed with Exception.\nDetails: {e}")
            except Exception:
                pass
            tracker.end_crawl(website_url, success=False)
            return "fail"

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_row = {executor.submit(process_row, row): row for row in pending_rows}
        
        for future in concurrent.futures.as_completed(future_to_row):
            row = future_to_row[future]
            try:
                res = future.result()
                if res in ("success", "cached_success"):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"  [-] Worker exception for row {row[1]}: {e}")
                fail_count += 1

            
    print(f"\n[*] Crawl run summary for {state_name.title()}:")
    print(f"    - Attempted: {len(pending_rows)}")
    print(f"    - Succeeded: {success_count}")
    print(f"    - Failed: {fail_count}")

def main():
    parser = argparse.ArgumentParser(description="Crawls websites for contractors in a state database.")
    parser.add_argument("--state", type=str, default="all", help="State to crawl (e.g. georgia, texas, or 'all').")
    parser.add_argument("--db", type=str, help="Direct path to SQLite database. If omitted, uses unified database.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of sites to crawl in this batch.")
    parser.add_argument("--overwrite", action="store_true", help="Force crawling and overwrite existing cached files.")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers for parallel crawls.")
    
    args = parser.parse_args()
    
    state = args.state
    limit = args.limit
    overwrite = args.overwrite
    workers = args.workers
    
    if args.db:
        db_path = os.path.abspath(args.db)
    else:
        db_path = utils.get_unified_db_path()
        
    if not os.path.exists(db_path):
        print(f"[-] Error: Database not found at: {db_path}")
        sys.exit(1)
        
    print(f"[*] Target State Filter: {state.title()}")
    print(f"[*] Database Path: {db_path}")
    print(f"[*] Crawl Batch Limit: {limit}")
    print(f"[*] Overwrite Existing: {overwrite}")
    print(f"[*] Concurrent Workers: {workers}")
    
    crawl_state_websites(db_path, state, limit, overwrite, workers)

if __name__ == "__main__":
    main()
