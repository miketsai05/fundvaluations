# LOOP THROUGH EACH URL AND EXTRACT LVL3 INVESTMENT DATA

import requests
from os import path
import time
import pyautogui

import pandas as pd
import xml.etree.ElementTree as ET

def getLine(data1, label_str):
    """ Given SEC filing as data1, returns remainder of line starting with given string label_str"""

    startInd = data1.find(label_str)
    endInd = data1.find("\n", startInd)
    data2 = data1[startInd+len(label_str):endInd].strip()
    return data2

def getSection(data1, tag):
    """ Given SEC filing as data1, returns subsection of data1 between <tag> and </tag> inclusive"""

    startInd = data1.find(tag)
    endtag = tag[0] + "/" + tag[1:]
    endInd = data1.find(endtag) + len(endtag) + 1
    data2 = data1[startInd:endInd]
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

def getData(data1, df_cols, twolevel_cols, Lvl3only = True):
    """ Extracts relevant holding data given SEC filing data"""

    # Getting filing information
    accessNum = getLine(data1,"ACCESSION NUMBER:")
    valDate = getSection(data1, "<repPdDate>")[11:-13]
    fileDate = getLine(data1, "FILED AS OF DATE:")
    fileDate = fileDate[0:4]+'-'+fileDate[4:6]+'-'+fileDate[6:8]

    # Getting holding level information
    tag = "<invstOrSecs>"
    data2 = getSection(data1, tag)

    holdings = xml2list(data2, df_cols, twolevel_cols)
    if Lvl3only:
        holdings = [dict for dict in holdings if dict['fairValLevel']=='3']

    return accessNum, valDate, fileDate, holdings


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
        master_holdings = pd.DataFrame(columns=all_cols)

    lastCIK = "" #comment out

    # Loop through urls in master_urls and extract relevant SEC data from each filing
    # update master_urls row and append holdings data to master_holdings

    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})

    for ind in master_urls.index:

        if master_urls.loc[ind,'CIK'] != lastCIK: #comment out
            print(master_urls.loc[ind,'CIK']) #comment out

        if master_urls.loc[ind,'accessNum'] == None:

            if ind % 100 == 0:
                print(ind)  # comment out
                pyautogui.press('volumedown')
                time.sleep(0.5)
                pyautogui.press('volumeup')

            if ind % 1000 == 0:
                master_urls.to_pickle(urlfilename)
                master_holdings.to_pickle(holdingsfilename)

            #req = urllib.request.Request(master_urls.loc[ind,'filingURL'], headers={'User-Agent': 'Mozilla/5.0'})
            #data1 = urllib.request.urlopen(req).read().decode('utf-8')

            url = master_urls.loc[ind, 'filingURL']
            data1 = s.get(url).text

            accessNum, valDate, fileDate, holdings = getData(data1, df_cols, twolevel_cols)
            master_urls.loc[ind, 'accessNum'] = accessNum
            master_urls.loc[ind, 'valDate'] = valDate
            master_urls.loc[ind, 'fileDate'] = fileDate

            master_holdings = master_holdings.append(holdings, ignore_index = True)

        time.sleep(0.2) #SEC rate limit 10 requests / sec - slight buffer to be safe here

        lastCIK = master_urls.loc[ind,'CIK'] #comment out

    master_urls.to_pickle(urlfilename)
    master_holdings.to_pickle(holdingsfilename)

if __name__ == "__main__":
    main()


