# FOR GIVEN COMPANY - FIND RELEVANT SEC FILING DATA FROM MASTER_HOLDINGS.PKL

# set up pages with logos for all unicorns
#   doing top 30 first
# set up page for all other searches

# load master_unicorns

# match by searching name string for Company Name and AKAs
# fuzzy match legal name

import pandas as pd
import plotly
import plotly.express as px
import numpy as np


def find_records(co_name, aka, legal_name, search_legal=False, threshold=0.5):
    ''' Looks up relevant records from master_holdings.pkl'''

    # Should I pass in master_holdings as a dataframe rather than open each time?? TBD

    holdingsfilename = "master_holdings.pkl"
    master_holdings = pd.read_pickle(holdingsfilename)

    tmp1 = master_holdings[master_holdings['name'].str.lower().str.contains(co_name.lower())]
    tmp2 = pd.DataFrame(columns=master_holdings.columns)
    tmp3 = pd.DataFrame(columns=master_holdings.columns)

    if aka:
        aka_list = [item.strip() for item in aka.split(',')]
        for short_name in aka_list:
            tmp2.append(master_holdings[master_holdings['name'].str.lower().str.contains(short_name.lower())])

    # if search_legal:
        # to do - implement fuzzy search??

    all_records = tmp1.append(tmp2).append(tmp3)
    all_records = all_records.drop_duplicates()

    return all_records


def select_unicorns():

    unicornsfilename = 'master_unicorns.xlsx'
    master_unicorns = pd.read_excel(unicornsfilename)
    master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)

    tmp_list = []

    for i in range(0, 30):
        co_name = master_unicorns.loc[i, 'Company Name']
        aka = master_unicorns.loc[i, 'aka']
        legal_name = master_unicorns.loc[i, 'Legal Name']

        tmp = find_records(co_name, aka, legal_name)
        tmp['unicorn'] = co_name

        tmp_list.append(tmp)

    select_holdings = pd.concat(tmp_list, ignore_index=True)

    holdings_cols = ['accessNum', 'name', 'title', 'balance', 'curCd', 'valUSD', 'unicorn']
    cik_cols = ['CIK', 'fundManager', 'Fund']

    cikfilename = "master_ciks.pkl"
    master_ciks = pd.read_pickle(cikfilename)

    urlfilename = "master_urls.pkl"
    master_urls = pd.read_pickle(urlfilename)

    unicorn_data = select_holdings[holdings_cols]
    unicorn_data = unicorn_data.merge(master_urls, how='left', on='accessNum')
    unicorn_data = unicorn_data.merge(master_ciks[cik_cols], how='left', on='CIK')

    numcols = ['balance','valUSD']
    unicorn_data[numcols] = unicorn_data[numcols].astype(float)

    datecols = ['valDate', 'fileDate']
    for i in range(len(datecols)):
        unicorn_data[datecols[i]] = pd.to_datetime(unicorn_data[datecols[i]])

    unicorn_data['pershare'] = (unicorn_data['valUSD']/unicorn_data['balance']).round(2)

    # Concatenate Fund and Series before groupby

    cols = ['unicorn', 'fundManager', 'valDate', 'pershare']
    f = {'balance': 'sum', 'Fund': ',<br>'.join, 'name':','.join, 'title':','.join, 'filingURL':','.join}

    unicorn_data_grouped = unicorn_data.groupby(cols, as_index=False).agg(f)
    unicorn_data_grouped['normbalance'] = np.log10(unicorn_data_grouped['balance']) # unicorn_data_grouped['balance']**0.35

    unicorn_data.to_pickle('unicorn_data')
    unicorn_data_grouped.to_pickle('unicorn_data_grouped')


def gen_fig(unicorn_name):

    unicorn_data_grouped = pd.read_pickle('unicorn_data_grouped')
    gdata = unicorn_data_grouped[unicorn_data_grouped['unicorn'] == unicorn_name].copy()
    gdata['valDatestr'] = gdata['valDate'].dt.strftime('%b %d, %Y')

    fig = px.scatter(gdata,
                     x='valDate',
                     y='pershare',
                     title=unicorn_name,
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

def gen_graph(unicorn_name):
    fig = gen_fig(unicorn_name)
    plotly.offline.plot(fig, filename='plotlygraph.html')

    # Separate each Fund Manager into a different trace so hover works even if same per share valuation
    # Fund Manager specific color throughout
    # Facet Row by fund manager
    # add annotations for funding round


# fig.update_traces(hovertemplate = '<b>%{hovertext}</b><br>Valuation Date = %{x}<br>Per Share Valuation = %{y}<br>Number of Shares = %{hover_data[0]}')

if __name__ == "__main__":
    select_unicorns()
    unicorn_data = pd.read_pickle('unicorn_data')
    gen_graph('Bytedance')

#import plotly.express as px
#xxx = select_unicorns[select_unicorns['Unicorn Name']=='Bytedance'].copy()
#xxx['Per Share']=xxx['valUSD'].astype(float)/xxx['balance'].astype(float)
#pdata = xxx[['valDate','pershare']].copy()
#pdata.valDate = pd.to_datetime(pdata.valDate)
#import plotly
#plotly.offline.plot(fig, filename='plotlygraph.html')
#yyy = xxx.groupby(['Manager Name','valDate','pershare','name','title'], as_index=False).agg({'balance':'sum', 'Fund':','.join})

# Data i need:
# From select_unicorns: AccessNum, Name, Title, balance, curCd, valUSD, Unicorn Name
# From master_urls: CIK, filingURL, AccessNum, valDate, fileDate (ALL COLUMNS)
# From master_ciks: CIK, Manager Name, Fund

# CHECK SPACE X