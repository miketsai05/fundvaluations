""" Scripts to run program related to CIK level data
# Cadence: Annually??
# Reads in SEC Excel file with all mutual fund CIKs
# Checks latest NCEN for fund family data
# Checks NPORT for level 3 holdings

check_ncen():
    - loops through latest NCEN, extract fund family data

check_lvl3():
    - loops through specific NPORT filing, checks for level 3 holdings

map_fundManager(tmpoverride=True):
    - maps fund families from master_funds.xlsx
    - copies unknown fund family to clipboard

# Notes:
# CIK Number: no leading zeros
# CIK: 10 digits - include leading zeros

# TO DO finish check_fundManager()

"""


from os import path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

import pandas as pd
import numpy as np
import requests
import pyautogui

from data.get_sec_data import get_line



def create_dfs(overwrite=False):

    cikfilename = 'master_ciks.pkl'
    cikexcel = 'master_ciks.xlsx'  # Excel file from SEC
    cik_cols = ['CIK', 'infamily', 'fundfamily', 'ncen_date', 'ncen_url', 'new_ncen', 'lvl3']
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
    """ Given text data from NCEN filing, returns 3 outputs related to fund family data
            - filing date
            - in family: Y/N
            - fund family
    """

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


def check_ncen():
    # loop through CIK, pull latest N-CEN FORM. check for fund family
    # check annually when SEC releases mutual fund file
    # need to loop until no errors - all mutual funds should have ncen

    tic = time.time()

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)
    master_ciks['ncen_date'] = pd.to_datetime(master_ciks['ncen_date'])
    keepcols = master_ciks.columns

    ncenfilename = 'master_ncens.pkl'
    master_ncens = pd.read_pickle(ncenfilename)
    master_ncens['fileDate'] = pd.to_datetime(master_ncens['fileDate'])
    latest_ncens = master_ncens.loc[master_ncens.reset_index().groupby('CIK')['fileDate'].idxmax()]

    cols_rename = {'CIK':'CIK Number', 'fileDate':'ncen_date', 'filingURL':'ncen_url'}
    latest_ncens.rename(columns=cols_rename, inplace=True)

    master_ciks = master_ciks.merge(latest_ncens, how='left', on='CIK Number', suffixes=('','_y'))
    ind1 = (master_ciks['ncen_date'] != master_ciks['ncen_date']) & (master_ciks['ncen_date_y'] == master_ciks['ncen_date_y'])
    ind2 = master_ciks['ncen_date_y'] > master_ciks['ncen_date']
    replace_ind =  ind1 | ind2
    master_ciks.loc[replace_ind, 'ncen_date'] = master_ciks.loc[replace_ind, 'ncen_date_y']
    master_ciks.loc[replace_ind, 'ncen_url'] = master_ciks.loc[replace_ind, 'ncen_url_y']
    master_ciks.loc[replace_ind, 'new_ncen'] = replace_ind[replace_ind]

    master_ciks = master_ciks[keepcols]

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    numcik = 0

    for index, row in master_ciks.iterrows():

        if row['new_ncen']:
            url = row['ncen_url']
            if url == url:
                data1 = s.get(url).text
                filedate, infam, fam = get_ncen_data(data1)
                master_ciks.loc[index, ['infamily', 'fundfamily', 'new_ncen']] = infam, fam, False
                numcik += 1
                time.sleep(0.2)

        if numcik % 50 == 0:
            print('Currently on ', index, ' of ', len(master_ciks))  # comment out
            pyautogui.press('volumedown')
            time.sleep(0.5)
            pyautogui.press('volumeup')

        if numcik % 500 == 0:
            master_ciks.to_pickle(cikfilename)

    master_ciks.to_pickle(cikfilename)
    toc = time.time()
    print('Looped through', numcik, 'CIKs in', toc-tic, 'secs.')


def check_lvl3(check_date=datetime(2020, 12, 31), date_delta=3, check='nan'):
    """
    # Inputs:
        # check_date: beginning of date range to filter by filing date
        # date_delta: range of dates to filter by filing date
        # check: if 'nan' - only checks 'nan' entries in lvl3 column, else checks both nan or False

    # get all nport filings for 12/31/2020 date - check level 3 there.
    """

    tic = time.time()

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    urlfilename = 'master_urls.pkl'
    master_urls = pd.read_pickle(urlfilename)
    master_urls['fileDate'] = pd.to_datetime(master_urls['fileDate'])

    ind = (master_urls['fileDate'] > check_date) & (master_urls['fileDate'] <= (check_date+relativedelta(months=date_delta)))
    urlset = master_urls.loc[ind]

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    numcik = 0

    for index, row in master_ciks.iterrows():

        if check == 'nan':
            proceed_check = row['lvl3'] != row['lvl3']
        else:
            proceed_check = (row['lvl3'] != row['lvl3']) or (row['lvl3'] is False)

        if proceed_check:

            currCIK = row['CIK Number']
            nport_urls = list(urlset[urlset['CIK Number'] == currCIK]['filingURL'])

            print(currCIK, len(nport_urls))

            if len(nport_urls) > 0:
                lvl3 = False
                for url in nport_urls:
                    lvl3 = lvl3 or s.get(url).text.find('<fairValLevel>3</fairValLevel>') > 0
                    time.sleep(0.2)
                master_ciks.loc[index, 'lvl3'] = lvl3  # has lvl3 = true, does not have lvl3 = false, no nport = nan
                numcik += 1

        if (numcik>0) & (numcik % 50 == 0):
            print('Currently on ', index, ' of ', len(master_ciks), '. Pulled ', numcik, ' so far')  # comment out
            pyautogui.press('volumedown')
            time.sleep(0.5)
            pyautogui.press('volumeup')

        if numcik % 500 == 0:
            master_ciks.to_pickle(cikfilename)

    master_ciks.to_pickle(cikfilename)

    toc = time.time()

    print('Looped through', numcik, 'CIKs in', toc-tic, 'secs')
    # only overwrite if not NAN!! - OK, only testing where lvl3=False
    # separate level 3? all done quarterly? run once through all?


def check_fundManager():

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    # MASTER HOLDINGS DATE --> MERGE
    # SELECT ROWS WHERE fundManager == nan

def map_fundManager(tmpoverride=True):

    cikfilename = 'master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    master_ciks['fundManager_raw'] = np.nan

    famind = master_ciks['fundfamily']==master_ciks['fundfamily']

    master_ciks.loc[famind, 'fundManager_raw'] = master_ciks.loc[famind, 'fundfamily']
    master_ciks.loc[~famind, 'fundManager_raw'] = master_ciks.loc[~famind, 'Entity Name']

    fund_map = pd.read_excel('master_funds.xlsx', sheet_name='allfund_map')
    fund_map.set_index('fundManager_raw', inplace=True)

    master_ciks['fundManager'] = master_ciks['fundManager_raw'].map(fund_map.squeeze())

    tmpind = master_ciks['fundManager'] != master_ciks['fundManager']
    if tmpoverride:
        master_ciks.loc[tmpind, 'fundManager'] = master_ciks.loc[tmpind, 'Entity Name']
    else:
        master_ciks[tmpind]['fundManager_raw'].value_counts().to_clipboard()
        print('test')

    master_ciks.to_pickle(cikfilename)


def main():

    if False:
        print('Looping through NCENs')
        check_ncen()

    if False:
        check_date = datetime(2019, 9, 30)
        date_delta = 3
        check = 'nan'
        print('Looping through CIKs to check for Level 3')
        check_lvl3(check_date=check_date, date_delta=date_delta, check=check)

    if True:
        tmpoverride=True
        map_fundManager(tmpoverride=tmpoverride)


if __name__ == "__main__":
    main()










# def check_ncen(subset='nan'):
#     # loop through CIK, pull latest N-CEN FORM. check for fund family
#     # check annually when SEC releases mutual fund file
#     # need to loop until no errors - all mutual funds should have ncen
#
#     tic = time.time()
#
#     cikfilename = 'master_ciks.pkl'
#     master_ciks = pd.read_pickle(cikfilename)
#
#     if subset=='all':
#         cikstopull = list(master_ciks['CIK Number'].astype(str))
#         rowidx = cikstopull.index
#         cikstopull = list(cikstopull.astype(str))
#     elif subset=='nan':
#         cikstopull = master_ciks[master_ciks['ncen_date']!=master_ciks['ncen_date']]['CIK Number']
#         rowidx = cikstopull.index
#         cikstopull = list(cikstopull.astype(str))
#
#     batch = 5
#     numcik = len(cikstopull)
#
#     s = requests.Session()
#     s.headers.update({'User-Agent': 'Mozilla/5.0'})
#
#     for i in range(math.ceil(numcik/batch)):
#
#         cikset = cikstopull[i*batch: min(numcik, (i+1)*batch)]
#         rowset = rowidx[i*batch: min(numcik, (i+1)*batch)]
#
#         print(cikset)
#         ncen_urls = Filing(cikset,
#                            filing_type=FilingType.FILING_NCEN,
#                            start_date=datetime(2019,1,1),
#                            end_date=datetime.today(),
#                            count=1).get_urls()
#
#         for cik, row in zip(cikset, rowset):
#             if len(ncen_urls[cik]) > 0:
#                 url = ncen_urls[cik][0]
#                 data1 = s.get(url).text
#                 filedate, infam, fam = get_ncen_data(data1)
#                 master_ciks.loc[row, ['infamily', 'fundfamily', 'ncen_date', 'ncen_url']] = infam, fam, filedate, url
#                 time.sleep(0.15)
#
#         time.sleep(1)
#
#     master_ciks.to_pickle(cikfilename)
#
#     toc = time.time()
#
#     num_nan_end = len(master_ciks[master_ciks['ncen_date']!=master_ciks['ncen_date']]['CIK Number'])
#     print('Looped through', numcik, 'CIKs in', toc-tic, 'secs. Number of nan entries remaining for NCEN data: ', num_nan_end)
#     return numcik-num_nan_end