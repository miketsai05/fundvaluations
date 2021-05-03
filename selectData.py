# FOR GIVEN COMPANY - FIND RELEVANT SEC FILING DATA FROM MASTER_HOLDINGS.PKL

#set up pages with logos for all unicorns
#   doing top 30 first
#set up page for all other searches

#load master_unicorns

#match by searching name string for Company Name and AKAs
#fuzzy match legal name

import pandas as pd

unicornsfilename = 'master_unicorns.xlsx'
master_unicorns = pd.read_excel(unicornsfilename)

def find_records(co_name, aka, legal_name, search_legal, threshold=0.5):
    ''' Looks up relevant records from master_holdings.pkl'''

    #Should I pass in master_holdings as a dataframe rather than open each time?? TBD

    holdingsfilename = "master_holdings.pkl"
    master_holdings = pd.read_pickle(holdingsfilename)

    tmp1 = master_holdings[master_holdings['name'].str.lower().str.contains(co_name.lower())]
    tmp2 = pd.DataFrame(columns=master_holdings.columns)
    tmp3 = pd.DataFrame(columns=master_holdings.columns)

    if aka:
        aka_list = [item.strip() for item in aka.split(',')]
        for short_name in aka_list:
            tmp2.append(master_holdings[master_holdings['name'].str.lower().str.contains(short_name.lower())])

    #if legalName:
        #to do - implement fuzzy search??

    all_records = tmp1.append(tmp2).append(tmp3)
    all_records.drop_duplicates()


def test():
    results = find_records('Bytedance',[],[],[])


    #REMOVE DUPLICATES FROM EXISTING PKL FILES
    #RENAME PKL FILES TO ALL LOWERCASE
