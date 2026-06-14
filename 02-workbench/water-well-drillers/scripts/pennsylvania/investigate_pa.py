import urllib.request
import ssl
from html.parser import HTMLParser
import re

url = "https://www.iframeapps.dcnr.pa.gov/topogeo/LicensedDriller"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class DCNRParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.table_depth = 0
        self.current_tag = None
        self.drillers = []
        
        # State machine variables
        self.in_main_row = False
        self.main_row_cols = []
        self.in_td_or_th = False
        self.cell_content = []
        
        self.in_child_grid = False
        self.child_headers = []
        self.child_values = []
        self.current_child_details = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attr_dict = dict(attrs)
        
        if tag == "table":
            self.table_depth += 1
            if attr_dict.get("id") == "LicensedDrillerTable":
                self.in_table = True
            elif self.in_table and attr_dict.get("class") == "ChildGrid":
                self.in_child_grid = True
                self.child_headers = []
                self.child_values = []
                
        elif self.in_table:
            if tag == "tr":
                if not self.in_child_grid and self.table_depth == 1:
                    self.in_main_row = True
                    self.main_row_cols = []
                    self.current_child_details = None
            elif tag in ("td", "th"):
                self.in_td_or_th = True
                self.cell_content = []
                    
    def handle_data(self, data):
        if self.in_td_or_th:
            self.cell_content.append(data)
            
    def handle_endtag(self, tag):
        if self.in_table:
            if tag in ("td", "th"):
                self.in_td_or_th = False
                text = "".join(self.cell_content).strip()
                if self.in_child_grid:
                    if tag == "th":
                        self.child_headers.append(text)
                    elif tag == "td":
                        self.child_values.append(text)
                else:
                    if self.in_main_row:
                        self.main_row_cols.append(text)
                        
            elif tag == "tr":
                if self.in_main_row and not self.in_child_grid and self.table_depth == 1:
                    self.in_main_row = False
                    # Col 0: plus image, Col 1: Company, Col 2: City, Col 3: State, Col 4: Phone
                    if len(self.main_row_cols) >= 5:
                        self.drillers.append({
                            "company": self.main_row_cols[1],
                            "city": self.main_row_cols[2],
                            "state": self.main_row_cols[3],
                            "phone": self.main_row_cols[4],
                            "details": self.current_child_details or {}
                        })
                        self.current_child_details = None
                        
            elif tag == "table":
                self.table_depth -= 1
                if self.in_child_grid and self.table_depth == 1:
                    self.in_child_grid = False
                    if self.child_headers and self.child_values:
                        details = {}
                        for h, v in zip(self.child_headers, self.child_values):
                            details[h] = v
                        self.current_child_details = details
                elif self.table_depth == 0:
                    self.in_table = False

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8')
        
        parser = DCNRParser()
        parser.feed(html)
        
        valid_drillers = [d for d in parser.drillers if d["company"].lower() != "company"]
        
        print(f"Parsed {len(valid_drillers)} valid drillers (excluding header).")
        if valid_drillers:
            print("\nFirst 3 drillers:")
            for d in valid_drillers[:3]:
                print(d)
            print("\nLast 2 drillers:")
            for d in valid_drillers[-2:]:
                print(d)
except Exception as e:
    print(f"Error: {e}")
