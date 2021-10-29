Order to update:

Quarterly / Monthly
1. Save latest .idx file from SEC website (https://www.sec.gov/Archives/edgar/full-index/)
2. Run load_urls
3. Run get_sec_data
4. Run get_cb_data
5. Run select_data
6. Update navbar.py footnote to current date

Annual
1. Download latest SEC mutual fund Excel file **needs work to automate here
2. Run load_ciks

After running updates:
1. Commit changes to github
2. Deploy latest to Heroku

------------------------------------------------------------------------------

Data Module Overview

ETL Data
/filings/
    - load_ciks.py -
    - load_urls.py
    - get_sec_data.py
    - get_cb_data.py

    Data Pkl
    - master_ciks.pkl
    - master_holdings.pkl
    - master_ncens.pkl
    - master_urls.pkl

    Data Input Excel
    - master_ciks.xlsx
    - master_funds.xlsx
    - master_unicorns.xlsx

    Output Pkl
    - unicorn_summary.pkl
    - unicorn_data.pkl
    - unicorn_data_grouped.pkl

select_data

------------------------------------------------------------------------------

ETL Data
/filings/
    - load_ciks.py
        - loops through latest NCEN, extract fund family data
        - loops through specific NPORT filing, checks for level 3 holdings
        - maps fund families from master_funds.xlsx
        - copies unknown fund family to clipboard
    - load_urls.py
        - opens idx file, saves NPORT filings
        - opens idx file, saves NCEN filings
    - get_sec_data.py
        - loops through master_urls.pkl, extracts filing data and stores in master_holdings.pkl
    - get_cb_data.py
        - scraps cbinsights unicorn list, saves to master_unicorns.xlsx

    Data Pkls
    - master_ciks.pkl
        Reporting File Number
        CIK Number
        Entity Name
        Entity Org Type
        Address_1
        Address_2
        City
        State
        Zip Code
        CIK
        infamily
        fundfamily
        ncen_date
        ncen_url
        new_ncen
        lvl3
        fundManager_raw
        fundManager
    - master_holdings.pkl
        accessNum
        name
        lei
        title
        cusip
        balance
        units
        curCd
        valUSD
        pctVal
        payoffProfile
        assetCat
        issuerCat
        invCountry
        isRestrictedSec
        fairValLevel
        isin
        ticker
        other
        isCashCollateral
        isNonCashCollateral
        loanByFundCondition
        isLoanByFund
        loanVal
    - master_ncens.pkl
        CIK
        company_name
        form_type
        fileDate
        filingURL
    - master_urls.pkl
        CIK Number
        company_name
        filingURL
        form_type
        fileDate
        valDate
        accessNum
        seriesid
        seriesname

    Data Input Excel
    - master_ciks.xlsx
        - SEC Excel file with all mutual fund CIKs
    - master_funds.xlsx
        - reported fund family mapped to consolidated fund families
    - master_unicorns.xlsx
        - scrapped unicorn data from cbinsights, user can add search or exclusion terms

    Output Pkl
    - unicorn_summary.pkl
        - for unicorn summary tab - data table
    - unicorn_data.pkl
        - for unicorn data tab - data table
    - unicorn_data_grouped.pkl
        - for unicorn data tab - graph

select_data


