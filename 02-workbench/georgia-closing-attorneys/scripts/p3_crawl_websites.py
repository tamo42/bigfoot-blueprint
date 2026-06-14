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

# Database Configuration
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "data", "directory.sqlite")
CACHE_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "cache", "crawled_text", "georgia-closing-attorneys")
PROGRESS_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "cache", "crawl_progress.json")

# HTTP configurations
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}
TIMEOUT = 8

def get_base_domain(url):
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc

def clean_html_to_text(html_content):
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Strip boilerplate elements
    for element in soup(["script", "style", "nav", "footer", "header", "head", "noscript", "iframe", "svg"]):
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
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=True)
        response.raise_for_status()
        return response.text, response.url
    except requests.exceptions.SSLError:
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
    parsed = urlparse(url)
    path = parsed.path.lower()
    netloc = parsed.netloc.lower()
    
    if parsed.scheme not in ("http", "https"):
        return False
        
    social_domains = [
        "facebook.com", "twitter.com", "instagram.com", "youtube.com", 
        "linkedin.com", "yelp.com", "pinterest.com", "google.com"
    ]
    if any(sd in netloc for sd in social_domains):
        return False
        
    binary_extensions = [
        ".zip", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4", 
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".exe", ".tar", 
        ".gz", ".xml", ".json", ".txt", ".csv", ".msi"
    ]
    if any(path.endswith(ext) for ext in binary_extensions):
        return False
        
    skip_paths = ["wp-login", "wp-admin", "login", "admin", "checkout", "cart", "account", "signin", "signup"]
    if any(sp in path for sp in skip_paths):
        return False
        
    return True

def extract_internal_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    base_domain = get_base_domain(base_url)
    
    internal_links = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        
        if get_base_domain(full_url) == base_domain:
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            if is_valid_crawl_link(clean_url):
                internal_links.add(clean_url)
            
    scored_links = []
    keywords = ["service", "about", "practice", "real", "estate", "closing", "contact", "attorney", "law"]
    
    for link in internal_links:
        if urlparse(link).path in ("", "/"):
            continue
            
        score = 0
        path_lower = urlparse(link).path.lower()
        for kw in keywords:
            if kw in path_lower:
                score += 10
                
        score -= len(urlparse(link).path.split("/"))
        scored_links.append((link, score))
        
    scored_links.sort(key=lambda x: x[1], reverse=True)
    return [link for link, score in scored_links]

def crawl_contractor_site(website_url, output_path, failed_path):
    if not is_valid_crawl_link(website_url):
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(f"Crawl Failed: Invalid website link type. URL: {website_url}")
        print(f"  [-] Skipped invalid website type: {website_url}")
        return False

    print(f"[*] Crawling: {website_url}...")
    
    html, resolved_url = fetch_page(website_url)
    if not html:
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
    
    internal_links = extract_internal_links(html, resolved_url)
    target_links = internal_links[:4]
    
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
            time.sleep(0.5)
        else:
            print(f"    [-] Failed to crawl subpage {link}: {sub_err}")
            
    line_counts = {}
    for page in pages_content:
        for line in set(page["lines"]):
            line_counts[line] = line_counts.get(line, 0) + 1
            
    total_chars_raw = 0
    total_chars_cleaned = 0
    output_blocks = []
    
    for page in pages_content:
        raw_page_text = "\n".join(page["lines"])
        total_chars_raw += len(raw_page_text)
        
        if page["is_homepage"]:
            filtered_lines = page["lines"]
        else:
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
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"  [+] Saved crawled content to: {output_path}")
    savings = ((total_chars_raw - total_chars_cleaned) / max(1, total_chars_raw)) * 100
    print(f"      - Token/Char savings: {savings:.1f}%")
    return True

class CrawlProgressTracker:
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

def crawl_websites(limit, overwrite=False, max_workers=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, website_url 
        FROM attorneys 
        WHERE website_url IS NOT NULL 
          AND website_url != '' 
          AND website_url != 'NOT_FOUND'
    """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("[+] No websites to crawl in database.")
        return
        
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    
    pending_rows = []
    for row in rows:
        row_id, website_url = row
        output_path = os.path.join(CACHE_DIR, f"{row_id}.txt")
        failed_path = os.path.join(CACHE_DIR, f"{row_id}.failed")
        
        if overwrite:
            if os.path.exists(output_path): os.remove(output_path)
            if os.path.exists(failed_path): os.remove(failed_path)
            pending_rows.append((row_id, website_url, output_path, failed_path))
        else:
            if not os.path.exists(output_path) and not os.path.exists(failed_path):
                pending_rows.append((row_id, website_url, output_path, failed_path))
            
    print(f"[*] Found {len(rows)} records with websites, {len(pending_rows)} are pending crawl.")
    
    pending_rows = pending_rows[:limit]
    if not pending_rows:
        print("[+] All pending websites have already been crawled/attempted.")
        return
        
    if os.path.exists(PROGRESS_PATH):
        try: os.remove(PROGRESS_PATH)
        except Exception: pass
        
    tracker = CrawlProgressTracker(PROGRESS_PATH, len(pending_rows))

    print(f"[*] Starting crawl run for {len(pending_rows)} sites with {max_workers} workers...")
    success_count = 0
    fail_count = 0
    
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    
    def process_row(row):
        row_id, website_url, output_path, failed_path = row
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
                if res == "success":
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"  [-] Worker exception for ID {row[0]}: {e}")
                fail_count += 1

    print(f"\n[*] Crawl run summary:")
    print(f"    - Attempted: {len(pending_rows)}")
    print(f"    - Succeeded: {success_count}")
    print(f"    - Failed: {fail_count}")

def main():
    parser = argparse.ArgumentParser(description="Crawls websites for closing attorneys in Georgia.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of sites to crawl in this batch.")
    parser.add_argument("--overwrite", action="store_true", help="Force crawling and overwrite existing cached files.")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers for parallel crawls.")
    
    args = parser.parse_args()
    
    print(f"[*] Target DB: {DB_PATH}")
    print(f"[*] Batch Limit: {args.limit}")
    print(f"[*] Overwrite Existing: {args.overwrite}")
    print(f"[*] Concurrent Workers: {args.workers}")
    
    crawl_websites(args.limit, args.overwrite, args.workers)

if __name__ == "__main__":
    main()
