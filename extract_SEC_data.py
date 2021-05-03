# LOOP THROUGH EACH URL AND EXTRACT LVL3 INVESTMENT DATA

import requests
from os import path
import time
import pyautogui

import pandas as pd
import xml.etree.ElementTree as ET


def get_line(data1, label_str):
    """ Given SEC filing as data1, returns remainder of line starting with given string label_str"""

    start_ind = data1.find(label_str)
    end_ind = data1.find("\n", start_ind)
    data2 = data1[start_ind+len(label_str):end_ind].strip()
    return data2


def get_section(data1, tag):
    """ Given SEC filing as data1, returns subsection of data1 between <tag> and </tag> inclusive"""

    start_ind = data1.find(tag)
    endtag = tag[0] + "/" + tag[1:]
    end_ind = data1.find(endtag) + len(endtag) + 1
    data2 = data1[start_ind:end_ind]
    return data2


def xml2list(data2, df_cols, twolevel_cols):
    """ Given subsection of SEC filing data, parses XML data into list of lists

    Inputs:
    data2: <invstOrSecs> subsection of SEC filing
    df_cols: list of dataframe columns for dictionary where data is in first node level
    twolevel_cols: dict with keyword/column list pairing where data is in second node level
            function will first look for attribute, if none then check for value else returns None

    """

    all_cols = df_cols + sum(twolevel_cols.values(), [])
    rows = []

    text_root = ET.fromstring(data2)

    for node in text_root:

        sec = []

        for el in df_cols:
            if node.find(el) is not None:
                sec.append(node.find(el).text)
            else:
                sec.append(None)

        for level in twolevel_cols.keys():
            for el in twolevel_cols[level]:
                child = node.find(level).find(el)
                if child is not None:
                    if child.attrib.values():
                        sec.append(list(child.attrib.values()))
                        # print(child.attrib.values(), child.text) # NEED TO IMPROVE THIS FOR ATTRIBUTE "loanByFundCondition" also clean up identifier columns
                    else:
                        sec.append(child.text)
                else:
                    sec.append(None)

        curr_sec = {all_cols[i]: sec[i] for i, _ in enumerate(all_cols)}
        rows.append(curr_sec)

    return rows


def get_data(data1, df_cols, twolevel_cols, lvl3only=True):
    """ Extracts relevant holding data given SEC filing data"""

    # Getting filing information
    accessNum = get_line(data1, "ACCESSION NUMBER:")
    val_date = get_section(data1, "<repPdDate>")[11:-13]
    file_date = get_line(data1, "FILED AS OF DATE:")
    file_date = file_date[0:4]+'-'+file_date[4:6]+'-'+file_date[6:8]

    # Getting holding level information
    tag = "<invstOrSecs>"
    data2 = get_section(data1, tag)

    if data2 != '':
        holdings = xml2list(data2, df_cols, twolevel_cols)

        if lvl3only:
            holdings = [item for item in holdings if item['fairValLevel'] == '3']

        holdings = [dict(item, accessNum=accessNum) for item in holdings]

    else:
        print('SEC filing accession number: '+accessNum+' has no holdings data')
        holdings = {}

    return accessNum, val_date, file_date, holdings


def main():

    # Open master_urls and master_holdings pickle files
    urlfilename = "master_urls.pkl"
    master_urls = pd.read_pickle(urlfilename)

    holdingsfilename = 'master_holdings.pkl'

    df_cols = ["name", "lei", "title", "cusip", "balance", "units", "curCd", "valUSD", "pctVal", "payoffProfile",
               "assetCat", "issuerCat", "invCountry", "isRestrictedSec", "fairValLevel", ]

    id_cols = ["isin", "ticker", "other"]
    sec_lend_cols = ["isCashCollateral", "isNonCashCollateral", "loanByFundCondition", "isLoanByFund", "loanVal"]
    twolevel_cols = {"identifiers": id_cols, "securityLending": sec_lend_cols}

    all_cols = df_cols+id_cols+sec_lend_cols

    if path.exists(holdingsfilename):
        master_holdings = pd.read_pickle(holdingsfilename)
    else:
        master_holdings = pd.DataFrame(columns=['accessNum']+all_cols)

    lastcik = ""  #comment out

    # Loop through urls in master_urls and extract relevant SEC data from each filing
    # update master_urls row and append holdings data to master_holdings

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    for ind in master_urls.index:

        if master_urls.loc[ind, 'CIK'] != lastcik:  #comment out
            print(master_urls.loc[ind, 'CIK'])  #comment out

        if master_urls.loc[ind, 'accessNum'] == None:

            if ind % 100 == 0:
                print(ind)  # comment out
                pyautogui.press('volumedown')
                time.sleep(0.5)
                pyautogui.press('volumeup')

            if ind % 1000 == 0:
                master_urls.to_pickle(urlfilename)
                master_holdings.to_pickle(holdingsfilename)

            # if ind>=13144 and ind<13200:
            #     print(ind)

            url = master_urls.loc[ind, 'filingURL']
            data1 = s.get(url).text

            accessNum, val_date, file_date, holdings = get_data(data1, df_cols, twolevel_cols)
            master_urls.loc[ind, 'accessNum'] = accessNum
            master_urls.loc[ind, 'valDate'] = val_date
            master_urls.loc[ind, 'fileDate'] = file_date

            if holdings:
                master_holdings = master_holdings.append(holdings, ignore_index=True)

            time.sleep(0.2)  #SEC rate limit 10 requests / sec - slight buffer to be safe here

        lastcik = master_urls.loc[ind, 'CIK']  #comment out

    master_urls.to_pickle(urlfilename)
    master_holdings.to_pickle(holdingsfilename)


if __name__ == "__main__":
    main()
