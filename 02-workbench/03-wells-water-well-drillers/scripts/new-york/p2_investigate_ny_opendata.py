import urllib.request
import json

url = "https://data.ny.gov/api/views?q=water%20well"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req).read()
    data = json.loads(response)
    for view in data:
        print(view.get('id'), view.get('name'))
except Exception as e:
    print("Error:", e)
