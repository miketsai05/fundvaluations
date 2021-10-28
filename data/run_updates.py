"""
Order to update:

Quarterly / Monthly
1. Save latest .idx file from SEC website (https://www.sec.gov/Archives/edgar/full-index/)
2. Run load_urls
3. Run get_sec_data
4. Run get_cb_data
5. Run select_data

Annual
1. Download latest SEC mutual fund Excel file **needs work to automate here
2. Run load_ciks

After running updates:
1. Commit changes to github
2. Deploy latest to Heroku

"""

import datetime

def run_monthly():
    import load_urls
    import get_sec_data
    import get_cb_data
    import select_data

    # this should always be updated to roughly 5 months prior to current date
    # filings due 60 days after quarter end - so anything older than 5 months shouldn't be most recent data point anymore
    cutoffdate = datetime.date(2021, 5, 31)

    load_urls.main()
    get_sec_data.main()
    get_cb_data.main()
    select_data.main(cutoffdate)