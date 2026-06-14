import urllib.request
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    print("Link:", attr[1])

url = "https://appfactory.dec.ny.gov/WaterWell/Contractor_Search"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    print("Final URL:", response.geturl())
    html = response.read().decode('utf-8')
    parser = MyHTMLParser()
    parser.feed(html)
except Exception as e:
    print("Error:", e)
