import pandas as pd
import sqlite3
import os
from playwright.sync_api import sync_playwright

URL = "https://app.azwater.gov/DrillersList/"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, 'downloads')
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data'))
DB_PATH = os.path.join(DATA_DIR, 'arizona_wells.sqlite')

def scrape_arizona():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        print(f"Navigating to {URL}")
        page.goto(URL)
        
        print("Waiting for Export button...")
        # The button is likely an input or button with id containing btnExport
        with page.expect_download() as download_info:
            page.locator("input[id*='btnExport']").click()
        download = download_info.value
        
        download_path = os.path.join(DOWNLOAD_DIR, "arizona_drillers.xls")
        download.save_as(download_path)
        print(f"File downloaded to {download_path}")
        browser.close()
        
    return download_path

def clean_and_save(file_path):
    print("Reading file with pandas...")
    try:
        # ASP.NET commonly exports standard excel or html masquerading as xls
        try:
            df = pd.read_excel(file_path)
        except Exception:
            # Try html
            tables = pd.read_html(file_path)
            df = tables[0]
            
        print(f"Loaded {len(df)} records.")
        
        # Standardize columns
        col_mapping = {
            'NUM': 'license_number',
            'COMPANY': 'company_name',
            'ADDRESS1': 'address1',
            'ADDRESS2': 'address2',
            'CITY': 'city',
            'STATE': 'state',
            'ZIP': 'zip_code',
            'PHONE': 'phone',
            'ROC_LICENSES': 'roc_licenses',
            'QUALIFYING_PARTY': 'qualifying_party',
            'LICENSE_CURRENTLY_ACTIVE': 'license_status'
        }
        
        df = df.rename(columns=lambda x: str(x).strip().upper())
        new_cols = {}
        for c in df.columns:
            for k, v in col_mapping.items():
                if k == c:
                    new_cols[c] = v
                    break
        df = df.rename(columns=new_cols)
        
        if 'phone' in df.columns:
            df['phone'] = df['phone'].astype(str).str.replace(r'[^\d]', '', regex=True)
        
        df = df.fillna('')
        
        print("Saving to SQLite...")
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('arizona_well_drillers', conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"Successfully saved to {DB_PATH}")
        return len(df)
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return 0

if __name__ == "__main__":
    file_path = scrape_arizona()
    count = clean_and_save(file_path)
    print(f"Final Count: {count}")
