import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get('https://www.ncwelldriller.org/web/eh/find-contractor', verify=False, timeout=15, headers=headers)
    print("Status Code:", response.status_code)
    print("URL:", response.url)
    print(response.text[:2000])
except Exception as e:
    print(f"Error: {e}")
