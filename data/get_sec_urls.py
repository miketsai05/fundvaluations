#LOAD MUTUAL FUND CIKs, CHECK IF EACH MUTUAL FUND HAS LVL3 INVESTMENTS
# return most recent first
# startdate/endate relates to filing date

import pandas as pd
import numpy as np
import urllib

from secedgar.filings import Filing, FilingType
from os import path
from os import listdir
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from extract_sec_data import get_line
import requests


def create_dfs(overwrite=False):
    cikfilename = 'data/master_ciks.pkl'
    cikexcel = 'data/master_ciks.xlsx'
    cik_cols = ['CIK', 'infamily', 'fundfamily', 'ncen_date', 'ncen_url', 'get_urls_date', 'lvl3']
    if ~path.exists(cikfilename) or overwrite:
        master_ciks = pd.read_excel(cikexcel)
        master_ciks = master_ciks.reindex( columns=master_ciks.columns.tolist()+cik_cols)
        master_ciks['CIK'] = master_ciks['CIK Number'].zfill(10)
        master_ciks.to_pickle(cikfilename)

    urlfilename = 'data/master_urls.pkl'
    url_cols = ['CIK', 'filingURL', 'accessNum', 'seriesid', 'valDate', 'fileDate']
    if ~path.exists(urlfilename) or overwrite:
        master_urls = pd.DataFrame(columns=url_cols)
        master_urls.to_pickle(urlfilename)

    seriesexcel = 'data/master_______'


def get_ncen_data(data1):

    filedate = infam = fam = np.nan
    filedate = get_line(data1, 'FILED AS OF DATE:')
    tmpfam = get_line(data1, 'isRegistrantFamilyInvComp')
    if tmpfam[2]=='Y':
        infam = 'Y'
        fam = tmpfam[27:-3]
    elif tmpfam[1]=='N':
        infam = 'N'
    else:
        infam = 'flag'

    return filedate, infam, fam


def check_ncen():

    # separate CIK and Series - need to track both
    # loop through CIK, pull N-CEN FORM. check for fund family
    # get all nport filings for 12/31/2020 date - check level 3 there.
    # check annually when SEC releases mutual fund file

    cikfilename = 'data/master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    cikstopull = list(master_ciks['CIK Number'].astype(str))
    rowidx = list(master_ciks['CIK Number'].index)
    ncen_urls = Filing(cikstopull, filing_type=FilingType.FILING_NCEN, end_date=datetime.today(), count=1).get_urls()

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    for cik, row in zip(cikstopull, rowidx):
        url = ncen_urls[cik][0]
        data1 = s.get(url).text
        filedate, infam, fam = get_ncen_data(data1)
        master_ciks.loc[row, ['infamily', 'fundfamily', 'ncen_date', 'ncen_url']] = infam, fam, filedate, url

    #save master_ciks

# when looping through nport filings for filing url need to store SEries # in addition to val date

def check_lvl3(check_date=datetime(2020, 12, 31)):

    cikfilename = 'data/master_ciks.pkl'
    master_ciks = pd.read_pickle(cikfilename)

    cikstopull = list(master_ciks[master_ciks['lvl3']!=True]['CIK Number'].astype(str))
    rowidx = list(master_ciks[master_ciks['lvl3']!=True]['CIK Number'].index)
    nport_urls = Filing(cikstopull,
        filing_type=FilingType.FILING_NPORTP,
        count=1,
        start_date=check_date,
        end_date=check_date+relativedelta(months=3)).get_urls()

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    for cik, row in zip(cikstopull, rowidx):
        url = nport_urls[cik][0]
        lvl3 = s.get(url).text.find('<fairValLevel>3</fairValLevel>') > 0
        master_ciks.loc[row, 'lvl3'] = lvl3
        time.sleep(0.15)


    # only overwrite if not NAN!!
    # separate level 3? all done quarterly? run once through all?


def get_urls(end_date=datetime.today()):
    """Loops through each CIK in master_CIKs dataframe and requests all NPORTP urls
     from SEC since the get_urls_date. Stores urls in master_urls pkl
     [CIK, filing URL, accession number (None), valDate (None), fileDate(None)]
     last 3 items are None until data is pulled from SEC"""

    cikfilename = "master_ciks.pkl"
    master_ciks = pd.read_pickle(cikfilename)

    urlfilename = 'master_urls.pkl'
    master_urls = pd.read_pickle(urlfilename)

    new_urls = []

    #for ind, cik in master_CIKs.iloc[1:6].iterrows():
    for ind, cik in master_ciks.iterrows():

        not_updated = cik.get_urls_date is None or cik.get_urls_date < end_date
        if cik.lvl3 and not_updated:
            #to do - for buffer - subtract 1 year from start_date
            sec_urls = Filing(cik.CIK, filing_type=FilingType.FILING_NPORTP, start_date=cik.get_urls_date, end_date=end_date).get_urls()
            cik_urls = [[cik.CIK, x, None, None, None, None] for x in sec_urls[cik.CIK] if ~master_urls['filingURL'].str.contains(x).any()]
            new_urls += cik_urls
            master_ciks.loc[ind, 'get_urls_date'] = end_date

    new_urls = pd.DataFrame(new_urls, columns=master_urls.columns)
    master_urls = master_urls.append(new_urls, ignore_index=True)

    master_urls.to_pickle(urlfilename)
    master_ciks.to_pickle(cikfilename)


def main():

    load_new = 0
    if load_new:
        load_ciks()

    #to do - check if any master_CIKs have none in lvl3 col
    get_lvl3()

    end_date = datetime.today()

    get_urls(end_date)


if __name__ == "__main__":
    main()
