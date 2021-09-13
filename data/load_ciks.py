# TO DO finish check_fundManager()

# Cadence: Annually??
# Reads in SEC Excel file with all mutual fund CIKs
# Checks latest NCEN for fund family data
# Checks NPORT for level 3 holdings

# Notes:
# CIK Number: no leading zeros
# CIK: 10 digits - include leading zeros

import pandas as pd
import numpy as np
import math

from secedgar.filings import Filing, FilingType
from os import path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from data.get_sec_data import get_line
import requests
import pyautogui


def create_dfs(overwrite=False):

    cikfilename = 'master_ciks.pkl'
    cikexcel = 'master_ciks.xlsx'  # Excel file from SEC
    cik_cols = ['CIK', 'infamily', 'fundfamily', 'ncen_date', 'ncen_url', 'get_urls_date', 'lvl3']
    if ~path.exists(cikfilename) or overwrite:
        master_ciks = pd.read_excel(cikexcel)
        master_ciks = master_ciks.reindex( columns=master_ciks.columns.tolist()+cik_cols)
        master_ciks['CIK Number'] = master_ciks['CIK Number'].astype(str)
        master_ciks['CIK'] = master_ciks['CIK Number'].astype(str).str.zfill(10)
        master_ciks.to_pickle(cikfilename)

    urlfilename = 'master_urls.pkl'
    url_cols = ['CIK', 'filingURL', 'accessNum', 'seriesid', 'valDate', 'fileDate']
    if ~path.exists(urlfilename) or overwrite:
        master_urls = pd.DataFrame(columns=url_cols)
        master_urls.to_pickle(urlfilename)

    # seriesexcel = 'data/master_______'


def get_ncen_data(data1):

    fam = np.nan
    filedate = get_line(data1, 'FILED AS OF DATE:')
    tmpfam = get_line(data1, 'isRegistrantFamilyInvComp')
    if tmpfam[2] == 'Y':
        infam = 'Y'
        fam = tmpfam[28:-3]
    elif tmpfam[1] == 'N':
        infam = 'N'
    else:
        infam = 'flag'

    return filedate, infam, fam


def check_ncen(subset='nan'):
    # loop through CIK, pull latest N-CEN FORM. check for fund family
    # check annually when SEC releases mutual fund file
    # need to loop until no errors - all mutual funds should have ncen

    tic = time.time()

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    if subset=='all':
        cikstopull = list(master_ciks['CIK Number'].astype(str))
        rowidx = cikstopull.index
        cikstopull = list(cikstopull.astype(str))
    elif subset=='nan':
        cikstopull = master_ciks[master_ciks['ncen_date']!=master_ciks['ncen_date']]['CIK Number']
        rowidx = cikstopull.index
        cikstopull = list(cikstopull.astype(str))

    batch = 5
    numcik = len(cikstopull)

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    for i in range(math.ceil(numcik/batch)):

        cikset = cikstopull[i*batch: min(numcik, (i+1)*batch)]
        rowset = rowidx[i*batch: min(numcik, (i+1)*batch)]

        ncen_urls = Filing(cikset,
                           filing_type=FilingType.FILING_NCEN,
                           start_date=datetime(2019,1,1),
                           end_date=datetime.today(),
                           count=1).get_urls()

        for cik, row in zip(cikset, rowset):
            if len(ncen_urls[cik]) > 0:
                url = ncen_urls[cik][0]
                data1 = s.get(url).text
                filedate, infam, fam = get_ncen_data(data1)
                master_ciks.loc[row, ['infamily', 'fundfamily', 'ncen_date', 'ncen_url']] = infam, fam, filedate, url
                time.sleep(0.15)

        time.sleep(1)

    master_ciks.to_pickle(cikfilename)

    toc = time.time()

    num_nan_end = len(master_ciks[master_ciks['ncen_date']!=master_ciks['ncen_date']]['CIK Number'])
    print('Looped through', numcik, 'CIKs in', toc-tic, 'secs. Number of nan entries remaining for NCEN data: ', num_nan_end)
    return numcik-num_nan_end


def check_lvl3(subset='nan', check_date=datetime(2020, 12, 31)):

    # get all nport filings for 12/31/2020 date - check level 3 there.
    tic = time.time()

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    if subset == 'all':
        cikstopull = master_ciks[master_ciks['lvl3']!=True]['CIK Number']
        rowidx = cikstopull.index
        cikstopull = list(cikstopull.astype(str))
    elif subset == 'nan':
        cikstopull = master_ciks[master_ciks['lvl3']!=master_ciks['lvl3']]['CIK Number']
        rowidx = cikstopull.index
        cikstopull = list(cikstopull.astype(str))

    batch = 5
    numcik = len(cikstopull)

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    print('Looping through CIKs - ' + str(numcik))

    for i in range(math.ceil(numcik/batch)):

        if i % 10 == 0:
            print(i*5)  # comment out
            pyautogui.press('volumedown')
            time.sleep(0.5)
            pyautogui.press('volumeup')

        if i % 100 == 0:
            master_ciks.to_pickle(cikfilename)

        cikset = cikstopull[i*batch: min(numcik, (i+1)*batch)]
        rowset = rowidx[i*batch: min(numcik, (i+1)*batch)]

        nport_urls = Filing(cikset,
            filing_type=FilingType.FILING_NPORTP,
            start_date=check_date,
            end_date=check_date+relativedelta(months=4)).get_urls() #need to check all nportp filings for each cik

        for cik, row in zip(cikset, rowset):
            lvl3 = False
            if len(nport_urls[cik]) > 0:
                for url in nport_urls[cik]:
                    lvl3 = lvl3 or s.get(url).text.find('<fairValLevel>3</fairValLevel>') > 0
                    time.sleep(0.1)
                master_ciks.loc[row, 'lvl3'] = lvl3  # has lvl3 = true, does not have lvl3 = false, no nport = nan

        time.sleep(0.5)

    master_ciks.to_pickle(cikfilename)

    toc = time.time()

    num_nan_end = len(master_ciks[master_ciks['lvl3']!=master_ciks['lvl3']]['CIK Number'])
    print('Looped through', numcik, 'CIKs in', toc-tic, 'secs. Number of nan entries remaining for lvl3: ', num_nan_end)
    return numcik-num_nan_end
    # only overwrite if not NAN!! - OK, only testing where lvl3=False
    # separate level 3? all done quarterly? run once through all?



def check_fundManager():

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    # MASTER HOLDINGS DATE --> MERGE
    # SELECT ROWS WHERE fundManager == nan

def map_fundManager():

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    master_ciks['fundManager_raw'] = np.nan

    famind = master_ciks['fundfamily']==master_ciks['fundfamily']

    master_ciks.loc[famind, 'fundManager_raw'] = master_ciks.loc[famind, 'fundfamily']
    master_ciks.loc[~famind, 'fundManager_raw'] = master_ciks.loc[~famind, 'Entity Name']

    fund_map = pd.read_excel('data/master_funds.xlsx', sheet_name='allfund_map')
    fund_map.set_index('fundManager_raw', inplace=True)

    master_ciks['fundManager'] = master_ciks['fundManager_raw'].map(fund_map.squeeze())

    master_ciks.to_pickle(cikfilename)


def main():

    # load_new = 0
    # if load_new:
    #     load_ciks()

    if False:
        print('Looping through NCENs')
        ncen_nan_reduced = check_ncen()
        while ncen_nan_reduced > 0:
            ncen_nan_reduced = check_ncen()

    if False:
        print('Looping through CIKs to check for Level 3')
        lvl3_nan_reduced = check_lvl3()
        while lvl3_nan_reduced > 0:
            lvl3_nan_reduced = check_lvl3()



    # end_date = datetime.today()
    #
    # get_urls(end_date)


if __name__ == "__main__":
    main()
