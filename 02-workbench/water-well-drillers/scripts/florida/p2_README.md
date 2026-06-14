# Florida Water Well Contractors Ingestion Runbook (Planning)

Florida's licensing and regulation of water well construction is delegated by the Florida Department of Environmental Protection (DEP) to **five regional Water Management Districts (WMDs)** under Chapter 62-532 of the Florida Administrative Code. 

Because of this delegation, there is no single, centralized DEP contractor database. To build a comprehensive Florida registry, we must harvest and merge records from five separate regional sources or scrape the statewide license database.

---

## The 5 regional Water Management Districts

Each district regulates permitting and maintains its own active contractor directories:

1.  **Northwest Florida WMD (NWFWMD)**
    *   **Region:** Florida Panhandle (from Escambia to Jefferson County).
    *   **Portal:** [NWFWMD Well Construction](https://www.nwfwater.com/)
    *   **Data Format:** PDF and Excel directories of active regional licensees.

2.  **Suwannee River WMD (SRWMD)**
    *   **Region:** North-Central Florida (including Gainesville, Valdosta basin).
    *   **Portal:** [SRWMD Licensed Water Well Contractors](https://www.mysuwanneeriver.com/)
    *   **Data Format:** Searchable registry and downloadable CSV listing.

3.  **St. Johns River WMD (SJRWMD)**
    *   **Region:** Northeast and East-Central Florida (Jacksonville, Orlando, Daytona).
    *   **Portal:** [SJRWMD Permitting & Licensing](https://www.sjrwmd.com/)
    *   **Data Format:** Registry queries and local county health department delegacy databases.

4.  **Southwest Florida WMD (SWFWMD)**
    *   **Region:** West-Central Florida (Tampa Bay, Sarasota, Ocala).
    *   **Portal:** [SWFWMD Contractor Directories](https://www.swfwmd.state.fl.us/)
    *   **Data Format:** PDF roster managed by the Well Construction Section.

5.  **South Florida WMD (SFWMD)**
    *   **Region:** South Florida (Miami, Palm Beach, Fort Myers, Kissimmee).
    *   **Portal:** [SFWMD Water Well Contractors](https://www.sfwmd.gov/)
    *   **Data Format:** Dynamic search forms and downloadable XLS sheets.

---

## Harvesting Strategies

When developing Florida harvesting scripts in the future, choose between two strategies:

### Option A: Regional WMD Merging (Recommended for Contact Info)
*   **Method:** Write individual scrapers/parsers for each of the 5 WMD downloadable rosters (e.g., `scrape_srwmd.py`, `scrape_sfwmd.py`), consolidate them into a unified list, and deduplicate by license number (since licenses are valid statewide, some contractors appear in multiple WMD rosters).
*   **Pros:** Frequently includes local physical office addresses, phone numbers, and regional specializations.

### Option B: Statewide DBPR Portal Scrape
*   **Method:** Scrape the [Florida Department of Business & Professional Regulation (DBPR) License Portal](https://www.myfloridalicense.com/wl11.jsp) for all active licensees matching the "Water Well Contractor" class.
*   **Pros:** A single source of truth for licensing validity.
*   **Cons:** Often lacks operational business names or secondary branch phone numbers, typically providing mailing addresses.
