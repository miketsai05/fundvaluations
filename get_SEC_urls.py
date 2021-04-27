#LOAD MUTUAL FUND CIKs, CHECK IF EACH MUTUAL FUND HAS LVL3 INVESTMENTS
# GET 30 YEARS OF SEC NPORT FILINGS STARTING 1/1/1990 FOR FUNDS WITH LVL3

#pip install secedgar

import pandas as pd
import urllib

from secedgar.filings import Filing, FilingType
from os import path
from os import listdir
from datetime import datetime
import time


def loadCIKs():
    """Open each csv file in CIKs folder, extract CIKs and stores
     [10 digit CIK, Fund Manager Name, Fund, latest date for URL grab]
     in master_CIKs pkl for each fund manager"""

    #Open CIK pkl file
    filename = 'master_CIKs.pkl'
    CIK_cols = ['CIK','Name','Fund','get_urls_date','lvl3']

    if path.exists(filename):
        master_CIKs = pd.read_pickle(filename)
    else:
        master_CIKs = pd.DataFrame(columns=CIK_cols)

    #Loop through CIK csv files in CIKs folder and extract CIK info
    for csv_file in listdir('CIKs/'):

        fund_manager = csv_file.replace('.csv','').replace('_', ' ')

        f = open('CIKs/'+csv_file, 'r')
        all_ciks = f.read()
        f.close()

        all_ciks = all_ciks.splitlines()
        all_ciks = all_ciks[1:]
        all_ciks = [item.split(',',maxsplit=1) for item in all_ciks]
        all_ciks = [[item[0].zfill(10), fund_manager, item[1], datetime(1990,1,1), None] for item in all_ciks]

        new_ciks = pd.DataFrame([cik for cik in all_ciks if cik[0] not in list(master_CIKs.CIK)], columns=CIK_cols)

        master_CIKs = master_CIKs.append(new_ciks, ignore_index=True)

        master_CIKs.to_pickle(filename)


def getLvl3():
    """ Loop through each CIK in master_CIKs pkl file and check if each fund CIK contains and level 3 investments
    """

    CIKfilename = "master_CIKs.pkl"
    master_CIKs = pd.read_pickle(CIKfilename)

    #for given CIK check for level 3 if haven't previously checked for level 3
    for ind, cik in master_CIKs.iterrows():

        if cik.lvl3 is None:
            print(cik.CIK)
            master_CIKs.loc[ind,'lvl3'] = checkLvl3(cik.CIK)
            time.sleep(1)

    master_CIKs.to_pickle(CIKfilename)


def checkLvl3(cik, start_date = datetime(2020,11,30)):
    """Grabs 6 SEC filings iteratively and checks if this fund holds any Level 3 securities
     Returns True/False. Checks goes back every year until 2015 then every 5 years after that"""

    lvl3exists = False

    while not lvl3exists and start_date>datetime(1990,1,1):

        tmp_url = Filing(cik, filing_type=FilingType.FILING_NPORTP, start_date=start_date, count=1).get_urls()[cik]

        if tmp_url:
            req = urllib.request.Request(tmp_url[0], headers={'User-Agent': 'Mozilla/5.0'})
            lvl3exists = urllib.request.urlopen(req).read().decode('utf-8').find("<fairValLevel>3</fairValLevel>")>0

        if start_date.year>2015:
            start_date = datetime(start_date.year-1, start_date.month, start_date.day)
        else:
            start_date = datetime(start_date.year - 5, start_date.month, start_date.day)

        print(start_date)

    return lvl3exists


def getURLs(end_date = datetime.today()):
    """Loops through each CIK in master_CIKs dataframe and requests all NPORTP urls
     from SEC since the get_urls_date. Stores urls in master_urls pkl
     [CIK, filing URL, accession number (None), valDate (None), fileDate(None)]
     last 3 items are None until data is pulled from SEC"""

    CIKfilename = "master_CIKs.pkl"
    master_CIKs = pd.read_pickle(CIKfilename)

    new_urls = []

    #for ind, cik in master_CIKs.iloc[1:6].iterrows():
    for ind, cik in master_CIKs.iterrows():
        #print(ind)
        not_updated = cik.get_urls_date is None or cik.get_urls_date<end_date

        if cik.lvl3 and not_updated:
            sec_urls = Filing(cik.CIK, filing_type=FilingType.FILING_NPORTP, start_date=cik.get_urls_date, end_date=end_date).get_urls()
            cik_urls = [[cik.CIK, x, None, None, None] for x in sec_urls[cik.CIK]]
            new_urls += cik_urls
            master_CIKs.loc[ind,'get_urls_date'] = end_date

    filename = 'master_urls.pkl'
    url_cols = ['CIK', 'filingURL', 'accessNum', 'valDate', 'fileDate']
    if path.exists(filename):
        master_urls = pd.read_pickle(filename)
    else:
        master_urls = pd.DataFrame(columns=url_cols)

    new_urls = pd.DataFrame(new_urls, columns = url_cols)
    master_urls = master_urls.append(new_urls, ignore_index=True)

    master_urls.to_pickle(filename)
    master_CIKs.to_pickle(CIKfilename)



def main():

    load_new = 0
    if load_new:
        loadCIKs()

    #to do - check if any master_CIKs have none in lvl3 col
    getLvl3()

    end_date = datetime.today()

    getURLs(end_date)

def temp():
    CIKfilename = "master_CIKs.pkl"
    master_CIKs = pd.read_pickle(CIKfilename)

    urlfilename = "master_urls.pkl"
    master_urls = pd.read_pickle(urlfilename)

    holdingsfilename = "master_holdings.pkl"
    master_holdings = pd.read_pickle(holdingsfilename)

    master_CIKs = master_CIKs.iloc[0:94]
    master_CIKs.to_pickle(CIKfilename)

if __name__ == "__main__":
    main()
