# Pennsylvania Water Well Drillers Extraction Runbook

## Data Source
- **Agency:** Pennsylvania Department of Conservation and Natural Resources (DCNR), Bureau of Geological Survey
- **Source URL:** [Licensed Water Well Drillers Search](https://www.dcnr.pa.gov/Business/WaterWellDrillersLicensing/LicensedWaterWellDrillers/Pages/default.aspx)
- **Method:** Hunt down the search application/GIS endpoints and extract active driller license records.

## Setup & Execution
1. Run `investigate_pa.py` to identify the correct API or page structure for licensed drillers.
2. Run `scrape_pennsylvania.py` to fetch, sanitize, and insert the raw registry into `02-workbench/water-well-drillers/data/pennsylvania_wells.sqlite`.
