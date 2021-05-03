# FOR GIVEN COMPANY - FIND RELEVANT SEC FILING DATA FROM MASTER_HOLDINGS.PKL

#set up pages with logos for all unicorns
#   doing top 30 first
#set up page for all other searches

#load master_unicorns

#match by searching name string for Company Name and AKAs
#fuzzy match legal name

import pandas as pd

def find_records(co_name, aka, legal_name, search_legal=False, threshold=0.5):
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

    #if search_legal:
        #to do - implement fuzzy search??

    all_records = tmp1.append(tmp2).append(tmp3)
    all_records = all_records.drop_duplicates()

    return all_records

def main():

    unicornsfilename = 'master_unicorns.xlsx'
    master_unicorns = pd.read_excel(unicornsfilename)
    master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)

    tmp_list = []

    for i in range(0,30):
        co_name = master_unicorns.loc[i,'Company Name']
        aka = master_unicorns.loc[i,'aka']
        legal_name = master_unicorns.loc[i,'Legal Name']

        tmp = find_records(co_name, aka, legal_name)
        tmp['Unicorn Name'] = co_name

        tmp_list.append(tmp)

    select_holdings = pd.concat(tmp_list, ignore_index=True)

    holdings_cols = ['accessNum', 'name', 'title', 'balance', 'curCd', 'valUSD', 'Unicorn Name']
    cik_cols = ['CIK', 'Manager Name', 'Fund']

    cikfilename = "master_ciks.pkl"
    master_ciks = pd.read_pickle(cikfilename)

    urlfilename = "master_urls.pkl"
    master_urls = pd.read_pickle(urlfilename)

    select_unicorns = select_holdings[holdings_cols]
    select_unicorns = select_unicorns.merge(master_urls, how='left', on='accessNum')
    select_unicorns = select_unicorns.merge(master_ciks[cik_cols], how='left', on='CIK')

    select_unicorns.to_pickle('select_unicorns')

if __name__ == "__main__":
    main()
    select_unicorns = pd.read_pickle('select_unicorns')



# Data i need:
# From select_unicorns: AccessNum, Name, Title, balance, curCd, valUSD, Unicorn Name
# From master_urls: CIK, filingURL, AccessNum, valDate, fileDate (ALL COLUMNS)
# From master_ciks: CIK, Manager Name, Fund