# TO DO  add column to exclude certain keywords/phrases


# roadmap add annotations for funding round


import pandas as pd
import plotly.express as px
import numpy as np
import datetime



def search_select(search_name):
    """ Looks up relevant records from master_holdings.pkl given search term returns a copy of the data"""

    # Should I pass in master_holdings as a dataframe rather than open each time?? TBD

    holdingsfilename = "data/master_holdings.pkl"
    master_holdings = pd.read_pickle(holdingsfilename)

    ind1 = master_holdings['name'].str.lower().str.contains(search_name.lower())
    ind2 = master_holdings['title'].str.lower().str.contains(search_name.lower())

    search_results = master_holdings[ind1|ind2].copy()

    return search_results


def merge_data(select_holdings, unicornflag=False):
    """ Merges holding data with URL data and CIK data """

    holdings_cols = ['accessNum', 'name', 'title', 'balance', 'curCd', 'valUSD', 'units', 'assetCat']
    if unicornflag: holdings_cols.append('unicorn')

    cik_cols = ['CIK Number', 'CIK', 'Entity Name', 'infamily', 'fundfamily', 'fundManager', 'fundManager_raw']
    cikfilename = "data/master_ciks.pkl"
    master_ciks = pd.read_pickle(cikfilename)

    urlfilename = "data/master_urls.pkl"
    master_urls = pd.read_pickle(urlfilename)

    data_merged = select_holdings[holdings_cols]
    data_merged = data_merged.merge(master_urls, how='left', on='accessNum')
    data_merged = data_merged.merge(master_ciks[cik_cols], how='left', on='CIK Number')

    numcols = ['balance','valUSD']
    data_merged[numcols] = data_merged[numcols].astype(float)

    datecols = ['valDate', 'fileDate']
    for i in range(len(datecols)):
        data_merged[datecols[i]] = pd.to_datetime(data_merged[datecols[i]])

    data_merged['pershare'] = (data_merged['valUSD']/data_merged['balance']).round(2)

    return data_merged


def group_data(merged_data, group_on, unicornflag=False):
    """ Groups merged data for better visual in plotly graph. Converts certain columns and normalizes balance data
      From merged_data input: AccessNum, Name, Title, balance, curCd, valUSD, Unicorn Name
      From master_urls: CIK, filingURL, AccessNum, valDate, fileDate (ALL COLUMNS)
      From master_ciks: CIK, Manager Name, Fund """

    cols = [group_on] + ['valDate', 'pershare', 'units', 'assetCat']
    if unicornflag: cols = ['unicorn']+cols
    f = {'balance': 'sum', 'Entity Name': ',<br>'.join, 'seriesname': ',<br>'.join, 'name':','.join, 'title':','.join, 'filingURL':','.join}

    data_grouped = merged_data.groupby(cols, as_index=False).agg(f)
    data_grouped['normbalance'] = np.log10(data_grouped['balance'])

    return data_grouped


def search_unicorns(master_holdings, co_name, aka, legal_name, exclude, search_legal=False, threshold=0.5):
    """ Searches for relevant unicorn records in master_holdings.pkl given unicorn name, aka or legal name """

    ind1 = master_holdings['name'].str.lower().str.contains(co_name.lower())
    ind2 = pd.Series(np.full(len(master_holdings), False, dtype=bool), index=master_holdings.index)
    excludeind = pd.Series(np.full(len(master_holdings), False, dtype=bool), index=master_holdings.index)
    # ind3 = ind2

    if aka:
        aka_list = [item.strip() for item in aka.split(',')]
        for short_name in aka_list:
            ind2 = ind2 | (master_holdings['name'].str.lower().str.contains(short_name.lower()))

    # if search_legal:
        # to do - implement fuzzy search??

    if exclude:
        exclude_list = [item.strip() for item in exclude.split(',')]
        for exclude_name in exclude_list:
            excludeind = excludeind | master_holdings['name'].str.lower().str.contains(exclude_name.lower())

    final_ind = (ind1 | ind2) & (~excludeind)

    unicorn_records = master_holdings[final_ind].copy()

    return unicorn_records


#begindate, enddate, num=1

def select_unicorns(mindays=80, maxdays=100, cutoffdate = datetime.date(2020, 12, 31)):
    """ Loops through unicorns in master_unicorns.xlsx - searches for records.
    Concats all records, merges with URL and CIK data and groups by name, fund manager, valdate and price.
    Saves both selected merged records and grouped data"""

    holdingsfilename = "data/master_holdings.pkl"
    master_holdings = pd.read_pickle(holdingsfilename)

    unicornsfilename = 'data/master_unicorns.xlsx'
    master_unicorns = pd.read_excel(unicornsfilename)
    master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)
    unicornset = master_unicorns[0:30].copy()

    unicornset['increase'] = None
    unicornset['flat'] = None
    unicornset['decrease'] = None

    tmp_list = []

    for unicorn in unicornset.itertuples():
        co_name = unicorn[1] #unicorn['Company Name']
        aka = unicorn[2] #unicorn['aka']
        legal_name = unicorn[3] #unicorn['Legal Name']
        exclude = unicorn[4]

        tmp = search_unicorns(master_holdings, co_name, aka, legal_name, exclude)
        tmp['unicorn'] = co_name
        print(co_name)

        tmp_list.append(tmp)

    select_data = pd.concat(tmp_list, ignore_index=True)

    unicorn_data = merge_data(select_data, unicornflag=True)

    for unicorn in list(set(unicorn_data['unicorn'])):
        valdiff, datediff, increase, flat, decrease, num_outofQ = map_diff(unicorn_data[unicorn_data['unicorn']==unicorn], mindays, maxdays, cutoffdate)

        unicorn_data.loc[valdiff.index, 'QoQvaldiff'] = valdiff
        unicorn_data.loc[datediff.index, 'QoQdatediff'] = datediff
        unicornset.loc[unicornset['Company Name'] == unicorn, 'increase'] = increase
        unicornset.loc[unicornset['Company Name'] == unicorn, 'flat'] = flat
        unicornset.loc[unicornset['Company Name'] == unicorn, 'decrease'] = decrease
        if num_outofQ > 0:
            print('Excluded', num_outofQ, 'entries for ', unicorn)

    unicorn_data['QoQpercentdiff'] = unicorn_data['QoQvaldiff'].divide(unicorn_data['pershare'])

    unicorn_data_grouped = group_data(unicorn_data, 'fundManager', unicornflag=True)

    unicorn_summary = unicornset[['Company Name', 'Country', 'Industry', 'increase', 'flat', 'decrease']].copy()
    unicorn_summary.rename(columns={'Company Name': 'unicorn'}, inplace=True)

    f = {'accessNum': 'count',
         'fundManager': lambda x: ', '.join(x.astype(str).unique()),
         'valDate': ['min', 'max']}
    tmpgrouped = unicorn_data.groupby('unicorn', as_index=False).agg(f)
    tmpgrouped.columns = ["".join(x) for x in tmpgrouped.columns.ravel()]
    tmpgrouped['valDaterange'] = tmpgrouped['valDatemin'].astype(str) + ' to ' + tmpgrouped['valDatemax'].astype(str)
    tmpgrouped['valDatemin'] = tmpgrouped['valDatemin'].dt.strftime('%b %Y')
    tmpgrouped['valDatemax'] = tmpgrouped['valDatemax'].dt.strftime('%b %Y')
    # TO DO change this to Mmm YYYY

    # tmpgrouped.drop(columns=['valDatemin', 'valDatemax'], inplace=True)
    tmpgrouped.rename(columns={'fundManager<lambda>': 'fundManagerunique'}, inplace=True)

    unicorn_summary = unicorn_summary.merge(tmpgrouped, how='left', on='unicorn')

    unicorn_data.to_pickle('data/unicorn_data.pkl')
    unicorn_data_grouped.to_pickle('data/unicorn_data_grouped.pkl')
    unicorn_summary.to_pickle('data/unicorn_summary.pkl')


def map_diff( unicorn_subset , mindays, maxdays, cutoffdate):

    mindays = datetime.timedelta(days=mindays)
    maxdays = datetime.timedelta(days=maxdays)

    increase = flat = decrease = num_outofQ = 0
    valdiff = pd.Series()
    datediff = pd.Series()

    fundset = list(set(zip(unicorn_subset['CIK'], unicorn_subset['seriesid'], unicorn_subset['name'], unicorn_subset['title'])))

    for CIK, sid, inv_name, inv_title in fundset:

        ind1 = unicorn_subset['CIK'] == CIK
        ind2 = unicorn_subset['seriesid'] == sid
        ind3 = unicorn_subset['name'] == inv_name
        ind4 = unicorn_subset['title'] == inv_title
        ind = (ind1 & ind2 & ind3 & ind4)
        funddata = unicorn_subset[ind].sort_values(by='valDate')

        funddata.drop_duplicates(subset=['valDate','pershare'], inplace=True)

        if not funddata['valDate'].is_unique:
            print('Check ', CIK, sid, inv_name, inv_title)

        ddiff = funddata['valDate'].diff()
        vdiff = funddata['pershare'].diff()

        ind1 = ddiff < mindays
        ind2 = ddiff > maxdays
        ind = ind1 | ind2
        num_outofQ += sum(ind)

        if sum(ind) > 0:
            print('Excluding', sum(ind), 'entries - not quarter over quarter change for', CIK, sid, inv_name, inv_title)
            ddiff[ind] = np.nan
            vdiff[ind] = np.nan

        lastvalDate = funddata.tail(1)['valDate'].values[0]
        lastvdiff = vdiff.tail(1).values[0]

        if lastvalDate > pd.Timestamp(cutoffdate) and not np.isnan(lastvdiff):
            if lastvdiff > 0:
                increase += 1
            if lastvdiff == 0:
                flat += 1
            if lastvdiff < 0:
                decrease +=1

        datediff = datediff.append(ddiff)
        valdiff = valdiff.append(vdiff)

    return valdiff, datediff, increase, flat, decrease, num_outofQ



if __name__ == "__main__":
    select_unicorns()
    unicorn_data = pd.read_pickle('data/unicorn_data.pkl')
    unicorn_data_grouped = pd.read_pickle('data/unicorn_data_grouped.pkl')
    unicorn_summary = pd.read_pickle('data/unicorn_summary.pkl')
    # fundManager_unique = sorted(set(unicorn_data['fundManager_raw']))

