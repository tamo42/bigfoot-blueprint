import os
import re

CACHE_DIR = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\georgia-closing-attorneys\cache\crawled_text\georgia-closing-attorneys"

def analyze_cache():
    if not os.path.exists(CACHE_DIR):
        print("Cache directory not found.")
        return
        
    txt_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.txt')]
    
    bad_path_keywords = [
        "/blog", "/news", "/category", "/tag", "/author", "/archive", "/page/", 
        "comment", "/post/", "/feed/", "/rss/", "privacy", "terms", "disclaimer", 
        "cookie", "wp-json", "wp-content", "wp-includes", "xmlrpc", "trackback", 
        "_api", "_serverless", "_next", "_nuxt", "cdn-cgi", "replytocom",
        "/events/", "/calendar/", "/search", "/collections/", "/products/", 
        "/gallery/", "/portfolio/"
    ]
    
    stats = {kw: 0 for kw in bad_path_keywords}
    files_with_junk = 0
    total_junk_subpages = 0
    
    url_pattern = re.compile(r"=== SUBPAGE \((.*?)\) ===")
    
    for filename in txt_files:
        filepath = os.path.join(CACHE_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            subpages = url_pattern.findall(content)
            file_has_junk = False
            
            for url in subpages:
                url_lower = url.lower()
                is_junk = False
                for kw in bad_path_keywords:
                    if kw in url_lower:
                        stats[kw] += 1
                        is_junk = True
                
                if is_junk:
                    total_junk_subpages += 1
                    file_has_junk = True
                    
            if file_has_junk:
                files_with_junk += 1
                
        except Exception as e:
            pass
            
    print(f"Total Cache Files: {len(txt_files)}")
    print(f"Files Containing Junk Subpages: {files_with_junk}")
    print(f"Total Junk Subpages Identified: {total_junk_subpages}\n")
    
    print("Top Junk Path Keywords Found:")
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    for kw, count in sorted_stats:
        if count > 0:
            print(f"  {kw}: {count}")

if __name__ == "__main__":
    analyze_cache()
