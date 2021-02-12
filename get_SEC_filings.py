

#pip install secedgar

from secedgar.filings import Filing, FilingType
from secedgar.cik_lookup import CIKLookup

import urllib

import pandas as pd
import xml.etree.ElementTree as ET


def getSection(data1, tag):
    startInd = data1.find(tag)
    endtag = tag[0] + "/" + tag[1:]
    endInd = data1.find(endtag) + len(endtag) + 1
    data2 = data1[startInd:endInd]
    return data2

def xml2list(data2, df_cols, twolevel_cols):
    # df_cols should be list
    # twolevel_cols should be dict with keyword/column list pairing - first look for attribute, if none then check for value else returns None

    all_cols = df_cols + sum(twolevel_cols.values(), [])
    rows = []

    text_root = ET.fromstring(data2)

    for node in text_root:

        sec = []
        # print(node.find("name"))

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

def getLine(data1, label_str):
  startInd = data1.find(label_str)
  endInd = data1.find("\n",startInd)
  data2 = data1[startInd+len(label_str):endInd].strip()
  return data2

# Look up list of filing URLs

#fund_name = 'T. Rowe Price Science & Technology Fund, Inc.'
#cik = CIKLookup(['T. Rowe Price Science & Technology Fund, Inc.'])

# test_filing = Filing(cik,filing_type=FilingType.FILING_NPORT, start_date='20200630', count=2)

f = open('T_Rowe.txt', 'r')
all_ciks = f.read()
f.close()

all_ciks = all_ciks.splitlines()
all_ciks = all_ciks[1:]

ciks = [item.zfill(10) for item in all_ciks] #CIKLookup(all_ciks)

all_urls = Filing(ciks[70], filing_type=FilingType.FILING_NPORTP).get_urls() #break this up into multiple requests

print(all_urls)

# Start to loop through all filings

all_filings = []
all_holdings = []

for url in all_urls[ciks[70]]:

    file = urllib.request.urlopen(url)
    data1 = urllib.request.urlopen(url).read().decode('utf-8')

    # Getting general filing information

    tag = "<genInfo>"
    data2 = getSection(data1, tag)
    info_cols = ["regName", "regFileNumber", "regCik", "regLei", "regStreet1", "regCity", "regZipOrPostalCode",
                 "regPhone", "seriesName", "seriesId", "seriesLei", "repPdEnd", "repPdDate", "isFinalFiling"]

    text_root = ET.fromstring(data2)
    filingInfo = []

    for el in info_cols:
        if text_root.find(el) is not None:
            filingInfo.append(text_root.find(el).text)
        else:
            filingInfo.append(None)

    acc_num = getLine(data1,"ACCESSION NUMBER:")
    curr_date = curr_filing["repPdDate"]

    curr_filing = {info_cols[i]: filingInfo[i] for i, _ in enumerate(info_cols)}
    curr_filing["FilingURL"] = url
    curr_filing["accessNum"] = acc_num
    curr_filing["fileDate"] = getLine(data1, "FILED AS OF DATE:")
    all_filings.append(curr_filing)

    # Getting holding level information

    tag = "<invstOrSecs>"
    data2 = getSection(data1, tag)

    df_cols = ["name", "lei", "title", "cusip", "balance", "units", "curCd", "valUSD", "pctVal", "payoffProfile",
               "assetCat", "issuerCat", "invCountry", "isRestrictedSec", "fairValLevel", ]
    id_cols = ["isin", "ticker", "other"]
    sec_lend_cols = ["isCashCollateral", "isNonCashCollateral", "loanByFundCondition", "isLoanByFund", "loanVal"]

    twolevel_cols = {"identifiers": id_cols, "securityLending": sec_lend_cols}

    rows = xml2list(data2, df_cols, twolevel_cols)

    for item in rows:
      item.update({"ValuationDate": curr_date, "accessNum": acc_num})

    all_holdings = all_holdings + rows

all_filings = pd.DataFrame(all_filings, columns=info_cols + ["FilingURL", "accessNum", "fileDate"])

all_holdings = pd.DataFrame(all_holdings, columns=df_cols + id_cols + sec_lend_cols + ["ValuationDate", "accessNum"])

print(all_filings.head())
print(all_holdings.head())

# level3 = all_holdings[all_holdings["fairValLevel"] == "3"]

# print(all_holdings.size)
# all_holdings.head(5)

# print(level3.size)
# level3.head()

# len(level3)
# print(level3.ValuationDate)

# # Get security level info - TESTING ONLY
#
# tag = "<invstOrSecs>"
# data2 = getSection(data1, tag)
#
# df_cols = ["name", "lei", "title", "cusip", "balance", "units", "curCd", "valUSD", "pctVal", "payoffProfile",
#            "assetCat", "issuerCat", "invCountry", "isRestrictedSec", "fairValLevel", ]
# id_cols = ["isin", "ticker", "other"]
# sec_lend_cols = ["isCashCollateral", "isNonCashCollateral", "loanByFundCondition", "isLoanByFund", "loanVal"]
#
# twolevel_cols = {"identifiers": id_cols, "securityLending": sec_lend_cols}
#
# rows = xml2list(data2, df_cols, twolevel_cols, curr_date)
#
# test = pd.DataFrame(rows, columns=df_cols + id_cols + sec_lend_cols + ["ValuationDate"])
#
# test.head(10)

# whos