import urllib.request

URL = "https://www.dpor.virginia.gov/sites/default/files/Records%20and%20Documents/Regulant%20List/2705b__crnt.txt"

def main():
    print(f"Streaming first 100 lines from {URL}...")
    try:
        req = urllib.request.Request(
            URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            count = 0
            for line in response:
                if count >= 100:
                    break
                
                # Try decoding with utf-8, fallback to windows-1252
                try:
                    decoded = line.decode('utf-8')
                except UnicodeDecodeError:
                    decoded = line.decode('windows-1252', errors='replace')
                
                print(f"{count:02d}: {decoded.rstrip()}")
                count += 1
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == '__main__':
    main()
