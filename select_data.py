# NEED TO DISTINGUISH ==>>
# UNITS = NS is number of shares,
#         PA is principal amount,
#         NC is number of contracts,
#         OU is other units
# assetCat =
        # 'ABS-CBDO' - ABS-collateralized bond/debt obligation
        #  'ABS-MBS' - ABS-mortgage backed security
        #  'ABS-O' - ABS-other
        #  'DBT' - debt
        #  'DCO' - derivative-commodity
        #  'DCR' - derivative-credit
        #  'DE' - derivative-equity
        #  'DIR' - derivative-interest rate
        #  'EC' - equity-common
        #  'EP' - equity preferred
        #  'LON' - loan
        #  'None'
        #  'SN' - structured note
        #  'STIV' - short-term investment vehicle (e.g., money market fund, liquidity pool, or other cash management vehicle

# Asset type (short-term investment vehicle (e.g., money market fund, liquidity pool,
# or other cash management vehicle), repurchase agreement, equity-common, equity-preferred,
# debt, derivative-commodity, derivative-credit, derivative-equity, derivative-foreign exchange,
# derivative-interest rate, derivatives-other, structured note, loan, ABS-mortgage backed security,
# ABS-asset backed commercial paper, ABS-collateralized bond/debt obligation, ABS-other,
# commodity, real estate, other). If “other,” provide a brief description.

# FOR GIVEN COMPANY - FIND RELEVANT SEC FILING DATA FROM MASTER_HOLDINGS.PKL

# set up pages with logos for all unicorns - doing top 30 first
# set up page for all other searches

# Fund Family: master_ciks['fundfamily']
# Fund Manager: master_ciks['Entity Name']
# Fund: master_urls['seriesname']

import pandas as pd
import plotly
import plotly.express as px
import numpy as np


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

    cik_cols = ['CIK Number', 'CIK', 'Entity Name', 'infamily', 'fundfamily']
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


def group_data(merged_data, unicornflag=False):
    """ Groups merged data for better visual in plotly graph. Converts certain columns and normalizes balance data
      From merged_data input: AccessNum, Name, Title, balance, curCd, valUSD, Unicorn Name
      From master_urls: CIK, filingURL, AccessNum, valDate, fileDate (ALL COLUMNS)
      From master_ciks: CIK, Manager Name, Fund """

    # Concatenate Fund and Series before groupby?

    cols = ['fundfamily', 'valDate', 'pershare']
    if unicornflag: cols = ['unicorn']+cols
    f = {'balance': 'sum', 'Entity Name': ',<br>'.join, 'seriesname': ',<br>'.join, 'name':','.join, 'title':','.join, 'filingURL':','.join}

    data_grouped = merged_data.groupby(cols, as_index=False).agg(f)
    data_grouped['normbalance'] = np.log10(data_grouped['balance'])

    return data_grouped


def search_unicorns(master_holdings, co_name, aka, legal_name, search_legal=False, threshold=0.5):
    """ Searches for relevant unicorn records in master_holdings.pkl given unicorn name, aka or legal name """

    # Should I pass in master_holdings as a dataframe rather than open each time?? TBD

    # holdingsfilename = "data/master_holdings.pkl"
    # master_holdings = pd.read_pickle(holdingsfilename)

    ind1 = master_holdings['name'].str.lower().str.contains(co_name.lower())
    ind2 = pd.Series(np.full(len(master_holdings), False, dtype=bool), index=master_holdings.index)
    # ind3 = ind2

    if aka:
        aka_list = [item.strip() for item in aka.split(',')]
        for short_name in aka_list:
            ind2 = ind2 | (master_holdings['name'].str.lower().str.contains(short_name.lower()))

    # if search_legal:
        # to do - implement fuzzy search??

    unicorn_records = master_holdings[ind1|ind2].copy()

    return unicorn_records


def select_unicorns():
    """ Loops through unicorns in master_unicorns.xlsx - searches for records.
    Concats all records, merges with URL and CIK data and groups by name, fund manager, valdate and price.
    Saves both selected merged records and grouped data"""

    holdingsfilename = "data/master_holdings.pkl"
    master_holdings = pd.read_pickle(holdingsfilename)

    unicornsfilename = 'data/master_unicorns.xlsx'
    master_unicorns = pd.read_excel(unicornsfilename)
    master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)

    tmp_list = []

    for i in range(0, 30):
        co_name = master_unicorns.loc[i, 'Company Name']
        aka = master_unicorns.loc[i, 'aka']
        legal_name = master_unicorns.loc[i, 'Legal Name']

        tmp = search_unicorns(master_holdings, co_name, aka, legal_name)
        tmp['unicorn'] = co_name
        print(co_name)

        tmp_list.append(tmp)

    select_data = pd.concat(tmp_list, ignore_index=True)

    unicorn_data = merge_data(select_data, unicornflag=True)
    unicorn_data_grouped = group_data(unicorn_data, unicornflag=True)

    unicorn_data.to_pickle('data/unicorn_data.pkl')
    unicorn_data_grouped.to_pickle('data/unicorn_data_grouped.pkl')


def gen_fig(unicorn_name):

    unicorn_data_grouped = pd.read_pickle('data/unicorn_data_grouped.pkl')
    gdata = unicorn_data_grouped[unicorn_data_grouped['unicorn'] == unicorn_name].copy()

    return gen_fig_fromgdata(gdata, unicorn_name)

def gen_fig_fromgdata(gdata, graphtitle=''):
    gdata['valDatestr'] = gdata['valDate'].dt.strftime('%b %d, %Y')

    fig = px.scatter(gdata,
                     x='valDate',
                     y='pershare',
                     title=graphtitle,
                     size='normbalance',
                     color='fundManager',
                     template='simple_white',
                     hover_name='fundManager',
                     custom_data=['valDatestr', 'balance', 'Fund']
                     )

    fig.update_layout(
            xaxis_title='Valuation Date',
            xaxis_tick0='1989-12-31',
            xaxis_dtick='M1',
            xaxis_tickformat='%b %d<br>%Y',
            yaxis_title='Per Share Valuation',
            yaxis_tickformat='$.2f',
            yaxis_rangemode='tozero',
            legend_title='Fund Manager',
            title={
                'x': 0.5,
                'y': 0.9,
                'xanchor': 'center',
                'yanchor': 'top',
                'font_family': 'Arial',
                'font_size': 28,
            }
    )

    fig.update_traces(
            #mode='lines+markers',
            #marker_symbol='square',
            #marker_opacity=1,
            opacity=0.6,
            hovertemplate=
                '<b>Fund Manager:</b> %{hovertext}<br>'
                '<b>Valuation Date:</b> %{customdata[0]}<br>'
                '<b>Per Share Valuation:</b> %{y:$0.2f}<br>'
                '<b>Aggregate Number of Shares:</b> %{customdata[1]:0,000}<br><br>'
                '<b>Held By:</b> <br>%{customdata[2]}'
                '<extra></extra>',
            hoverlabel=None
    )

    return fig


    # Separate each Fund Manager into a different trace so hover works even if same per share valuation
    # Fund Manager specific color throughout
    # Facet Row by fund manager
    # add annotations for funding round


if __name__ == "__main__":
    select_unicorns()
    unicorn_data = pd.read_pickle('data/unicorn_data.pkl')
    unicorn_data_grouped = pd.read_pickle('data/unicorn_data_grouped.pkl')

