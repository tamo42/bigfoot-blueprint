import urllib.request
import urllib.parse
import re

query = "site:dec.ny.gov water well contractor search tool"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    links = re.findall(r'href="([^"]+)"', html)
    for link in links:
        if 'dec.ny.gov' in link:
            print(link)
except Exception as e:
    print("Error:", e)
