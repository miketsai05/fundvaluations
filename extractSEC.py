# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 09:48:19 2021

@author: miket
"""

#pip install secedgar

from secedgar.filings import Filing, FilingType
from secedgar.cik_lookup import CIKLookup

import urllib

import pandas as pd
import xml.etree.ElementTree as ET

fund_name = 'T. Rowe Price Science & Technology Fund, Inc.'
testcik = CIKLookup(['T. Rowe Price Science & Technology Fund, Inc.'])
testcik.lookup_dict

test_filing = Filing(testcik,filing_type=FilingType.FILING_NPORT)

xxx = test_filing.get_urls()

print(xxx)

print(type(list(test_filing.get_urls().values())[0][0]))
url = xxx[fund_name][0]
print(url)

file = urllib.request.urlopen(url)
#type(file)

data1 = urllib.request.urlopen(url).read().decode('utf-8')
#print(data)

startInd = data1.find("<invstOrSecs>")
endInd = data1.find("</invstOrSecs>")+len("</invstOrSecs>")+1

z = len("</invstOrSecs>")

data1[endInd+len("</invstOrSecs>")]

data2 = data1[startInd:endInd]

text_root = ET.fromstring(data2)

df_cols = ["name", "lei", "title", "cusip", "balance", "units", "curCd", "valUSD", "pctVal", "payoffProfile", "assetCat", "issuerCat", "invCountry", "isRestrictedSec", "fairValLevel",]
id_cols = ["isin", "ticker","other"]
sec_lend_cols = ["isCashCollateral", "isNonCashCollateral", "isLoanByFund"]

all_cols = df_cols + id_cols + sec_lend_cols

rows = []

for node in text_root:
  
  s_name = node.find("name").text
  print(s_name)
  sec = []

  for el in df_cols:   
    if node.find(el) is not None:
      sec.append(node.find(el).text)
    else:
      sec.append(None)

  for el in id_cols:
    child = node.find("identifiers").find(el)
    if child is not None:
      sec.append(child.attrib.values())
    else:
      sec.append(None)

  for el in sec_lend_cols:
    child = node.find("securityLending").find(el)
    if child is not None:
      sec.append(child.text)
    else:
      sec.append(None)

  rows.append({all_cols[i]: sec[i] for i, _ in enumerate(all_cols)})

df = pd.DataFrame(rows, columns=all_cols)

df.head()