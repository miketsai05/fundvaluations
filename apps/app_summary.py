# type of investments
#trend?? - # marking up, # marking down - sort by biggest options, YoY, QoQ, MoM
#link each unicorn to individual page


import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import pandas as pd
import select_data as sd
import apps.navbar as nb

from app import app


def gen_summary_data():

    unicornsfilename = 'data/master_unicorns.xlsx'
    master_unicorns = pd.read_excel(unicornsfilename)
    master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)
    unicornset = master_unicorns.loc[0:30, 'Company Name']
    unicorn_data = pd.read_pickle('data/unicorn_data')

    tmptable1 = master_unicorns[master_unicorns['Company Name'].isin(unicornset)][['Company Name', 'Country', 'Industry']]
    tmptable1.rename(columns={'Company Name': 'unicorn'}, inplace=True)

    f = {'accessNum': 'count', 'fundManager': lambda x: ', '.join(x.unique()), 'valDate': ['min', 'max']}
    tmpgrouped = unicorn_data.groupby('unicorn', as_index=False).agg(f)
    tmpgrouped.columns = ["".join(x) for x in tmpgrouped.columns.ravel()]
    tmpgrouped['valDaterange'] = tmpgrouped['valDatemin'].astype(str)+' to ' + tmpgrouped['valDatemax'].astype(str)
    tmpgrouped.drop(columns=['valDatemin', 'valDatemax'], inplace=True)
    tmpgrouped.rename(columns={'fundManager<lambda>': 'fundManagerunique'}, inplace=True)

    tmptable1 = tmptable1.merge(tmpgrouped, how='left', on='unicorn')

    # Store this to open
    # types of investments, trend

    return tmptable1


def gen_table_format():

    cols = ['unicorn', 'Country', 'Industry', 'fundManagerunique', 'accessNumcount', 'valDaterange']
    colnames = ['Company', 'Country', 'Industry', 'Fund Managers', 'Number of Filings', 'Valuation Dates Available']
    coltype = ['text', 'text', 'text', 'text', 'numeric', 'text']
    colpresentation = ['input', 'input', 'input', 'input', 'input', 'input']

    dt_cols = [{'name': x, 'id': y, 'type': z, 'presentation': a} for x, y, z, a in
               zip(colnames, cols, coltype, colpresentation)]

    numformat = Format(precision=0, scheme=Scheme.fixed).group(True)

    dt_cols[3]['format'] = numformat

    return dt_cols


layout = html.Div([

    nb.gen_navbar(),

    dbc.Container(

        dt.DataTable(
            id='table1',
            data = gen_summary_data().to_dict('records'),
            # data = tmptable1.to_dict('records'),
            columns=gen_table_format(),
            style_header={'fontWeight': 'bold', 'whiteSpace': 'normal', 'padding-left': '5px', 'padding-right': '5px'},
            style_cell={'textAlign': 'center'},
            sort_action='native',
        ),
        style={'padding-top': '20px'}
    ),

    nb.gen_bottombar()

])


