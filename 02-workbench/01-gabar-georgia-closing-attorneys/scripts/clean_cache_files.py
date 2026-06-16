import os
import re

CACHE_DIR = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\01-gabar-georgia-closing-attorneys\cache\crawled_text\01-gabar-georgia-closing-attorneys"

def clean_cache():
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
    
    # Pattern matches the delimiter line. It captures the entire line.
    delimiter_pattern = re.compile(r"^(=== (?:HOMEPAGE|SUBPAGE) \(.*?\) ===)$", re.MULTILINE)
    
    files_cleaned = 0
    blocks_removed = 0
    
    for filename in txt_files:
        filepath = os.path.join(CACHE_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split content by delimiters
        parts = delimiter_pattern.split(content)
        
        # parts will be [pre-text (usually empty), delimiter, content, delimiter, content, ...]
        if not parts:
            continue
            
        new_parts = []
        # Add the first pre-text if it exists and isn't just whitespace
        if parts[0].strip():
            new_parts.append(parts[0])
            
        file_modified = False
        
        for i in range(1, len(parts), 2):
            delimiter = parts[i]
            block_content = parts[i+1] if i+1 < len(parts) else ""
            
            # Check if this block should be skipped
            is_junk = False
            if "SUBPAGE" in delimiter:
                url_lower = delimiter.lower()
                for kw in bad_path_keywords:
                    if kw in url_lower:
                        is_junk = True
                        break
            
            if is_junk:
                blocks_removed += 1
                file_modified = True
            else:
                new_parts.append(delimiter)
                new_parts.append(block_content)
                
        if file_modified:
            new_content = "".join(new_parts)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            files_cleaned += 1

    print(f"Cleanup Complete.")
    print(f"Files Modified: {files_cleaned}")
    print(f"Total Junk Blocks Removed: {blocks_removed}")

if __name__ == "__main__":
    clean_cache()
