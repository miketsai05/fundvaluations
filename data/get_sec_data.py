""" Scripts to run program related to extracting SEC data from filings
# Cadence: run whenever load_urls is run
# LOOP THROUGH EACH URL AND EXTRACT LVL3 INVESTMENT DATA

get_line(data1, label_str):
get_section(data1, tag):
xml2list(data2, df_cols, twolevel_cols):
get_data(data1, df_cols, twolevel_cols, lvl3only=True):
main():

# TO DO - check CIKs not in cik.pkl CIKs

"""

import time
import xml.etree.ElementTree as ET
from os import path

import pandas as pd
import pyautogui
import requests


def get_line(data1, label_str):
    """Given SEC filing as data1, returns remainder of line starting with given string label_str"""

    start_ind = data1.find(label_str)
    end_ind = data1.find("\n", start_ind)
    data2 = data1[start_ind + len(label_str) : end_ind].strip()
    return data2


def get_section(data1, tag):
    """Given SEC filing as data1, returns subsection of data1 between <tag> and </tag> inclusive"""

    start_ind = data1.find(tag)
    endtag = tag[0] + "/" + tag[1:]
    end_ind = data1.find(endtag) + len(endtag) + 1
    data2 = data1[start_ind:end_ind]
    return data2


def xml2list(data2, df_cols, twolevel_cols):
    """Given subsection of SEC filing data, parses XML data into list of lists

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
                        # print(child.attrib.values(), child.text)
                        # NEED TO IMPROVE THIS FOR ATTRIBUTE "loanByFundCondition" also clean up identifier columns
                    else:
                        sec.append(child.text)
                else:
                    sec.append(None)

        curr_sec = {all_cols[i]: sec[i] for i, _ in enumerate(all_cols)}
        rows.append(curr_sec)

    return rows


def get_data(data1, df_cols, twolevel_cols, lvl3only=True):
    """Extracts relevant holding data given SEC filing data"""

    # Getting filing information
    accessNum = get_line(data1, "ACCESSION NUMBER:")
    val_date = get_section(data1, "<repPdDate>")[11:-13]

    # Getting holding level information
    tag = "<invstOrSecs>"
    data2 = get_section(data1, tag)

    if data2 != "":
        holdings = xml2list(data2, df_cols, twolevel_cols)

        if lvl3only:
            holdings = [item for item in holdings if item["fairValLevel"] == "3"]

        holdings = [dict(item, accessNum=accessNum) for item in holdings]

    else:
        print("SEC filing accession number: " + accessNum + " has no holdings data")
        holdings = {}

    return accessNum, val_date, holdings


def main():
    # Load pickle files
    cikfilename = "master_ciks.pkl"
    master_ciks = pd.read_pickle(cikfilename)

    urlfilename = "master_urls.pkl"
    master_urls = pd.read_pickle(urlfilename)

    holdingsfilename = "master_holdings.pkl"

    df_cols = [
        "name",
        "lei",
        "title",
        "cusip",
        "balance",
        "units",
        "curCd",
        "valUSD",
        "pctVal",
        "payoffProfile",
        "assetCat",
        "issuerCat",
        "invCountry",
        "isRestrictedSec",
        "fairValLevel",
    ]

    id_cols = ["isin", "ticker", "other"]
    sec_lend_cols = [
        "isCashCollateral",
        "isNonCashCollateral",
        "loanByFundCondition",
        "isLoanByFund",
        "loanVal",
    ]
    twolevel_cols = {"identifiers": id_cols, "securityLending": sec_lend_cols}

    all_cols = df_cols + id_cols + sec_lend_cols

    if path.exists(holdingsfilename):
        master_holdings = pd.read_pickle(holdingsfilename)
    else:
        master_holdings = pd.DataFrame(columns=["accessNum"] + all_cols)

    # Loop through urls in master_urls and extract relevant SEC data from each filing
    # update master_urls row and append holdings data to master_holdings

    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})

    print(
        "Number of unaccessed urls",
        len(master_urls[master_urls["accessNum"] != master_urls["accessNum"]]),
    )
    prior_CIK = ""

    for ind in master_urls.index:
        if ind % 500 == 0:
            print(ind)  # comment out
            pyautogui.press("volumedown")
            time.sleep(0.5)
            pyautogui.press("volumeup")

        if ind % 1000 == 0:
            master_urls.to_pickle(urlfilename)
            master_holdings.to_pickle(holdingsfilename)

        curr_accessNum = master_urls.loc[ind, "accessNum"]
        curr_CIK = master_urls.loc[ind, "CIK Number"]
        CIKinpkl = len(master_ciks[master_ciks["CIK Number"] == curr_CIK]["lvl3"]) > 0

        if CIKinpkl and curr_CIK not in ["277751", "906185"]:
            if curr_accessNum != curr_accessNum and (
                master_ciks[master_ciks["CIK Number"] == curr_CIK]["lvl3"].item()
                is True
            ):
                print(ind)

                url = master_urls.loc[ind, "filingURL"]
                data1 = s.get(url).text

                master_urls.loc[ind, "seriesid"] = get_line(data1, "<SERIES-ID>")
                master_urls.loc[ind, "seriesname"] = get_line(data1, "<SERIES-NAME>")

                accessNum, val_date, holdings = get_data(data1, df_cols, twolevel_cols)
                master_urls.loc[ind, "accessNum"] = accessNum
                master_urls.loc[ind, "valDate"] = val_date

                if holdings:
                    master_holdings = master_holdings.append(
                        holdings, ignore_index=True
                    )

                time.sleep(
                    0.15
                )  # SEC rate limit 10 requests / sec - slight buffer to be safe here
        else:
            if prior_CIK != curr_CIK:
                print(curr_CIK, "not in pkl file")
                prior_CIK = curr_CIK

    master_urls.to_pickle(urlfilename)
    master_holdings.to_pickle(holdingsfilename)


if __name__ == "__main__":
    main()
