# Arizona Well Drillers Scraper

## Overview
This script automates the extraction of licensed water well drilling contractors from the Arizona Department of Water Resources (ADWR).

## Source
- **URL**: [https://app.azwater.gov/DrillersList/](https://app.azwater.gov/DrillersList/)
- **Data Format**: ASP.NET Web Application (RadGrid table).

## Extraction Method
The script uses **Playwright** to navigate to the ADWR website and simulate a click on the "Export to Excel" button (`#ctl00_ContentPlaceHolder1_btnExport`). This allows us to retrieve all records at once without paginating through the web grid.

1. **Download**: Playwright handles the headless browser navigation and download interception. The file is saved to the local `downloads` directory.
2. **Parsing**: The downloaded Excel file (which is sometimes HTML formatted depending on the ASP.NET version) is parsed using `pandas`.
3. **Cleaning**: Column headers are mapped to our standard schema (`license_number`, `company_name`, `address1`, `city`, `state`, `zip_code`, `phone`, etc.). Phone numbers are stripped of non-digit characters.
4. **Storage**: The final cleaned dataset is exported to `02-workbench/03-wells-water-well-drillers/data/arizona_wells.sqlite` as the `arizona_well_drillers` table.

## Execution
To run the scraper:
```bash
python arizona_scraper.py
```

## Migration
After the initial extraction is completed and data is cleaned (using the general cleaning scripts), you can append the data to the master directory database using the `migrate_arizona.py` script:
```bash
python migrate_arizona.py
```
This script handles mapping the local ADWR-specific fields to the consolidated `water_well_directory.sqlite` schema and properly formats `technician_licenses` child records.
