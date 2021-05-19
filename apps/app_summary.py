#list of unicorns
# list of unicorns
# investors
# number of filings
# range of valuation dates
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

def gen_table(unicorn_name):
    cols = ['unicorn', 'fundManager', 'valDate', 'pershare', 'balance', 'Fund', 'name', 'title', 'filingURL'] #don't need this in both functions
    tmptable = unicorn_data[unicorn_data['unicorn']==unicorn_name][cols].copy()
    tmptable['Fund_xml'] = '['+tmptable['Fund'].astype(str)+']('+tmptable['filingURL'].str[:-24]+'xslFormNPORT-P_X01/primary_doc.xml)'
    tmptable['Fund_html']= '['+tmptable['Fund'].astype(str)+']('+tmptable['filingURL'].astype(str)+')'
    tmptable['valDate'] = tmptable['valDate'].dt.date
    return tmptable


def gen_table_format():
    cols = ['unicorn', 'fundManager', 'valDate', 'pershare', 'balance', 'Fund_xml', 'name', 'title']
    colnames = ['Company', 'Fund Manager', 'Valuation Date', 'Per Share Valuation', 'Number of Shares', 'Fund',
                'Holding Name', 'Holding Title']
    coltype = ['text', 'text', 'datetime', 'numeric', 'numeric', 'text', 'text', 'text']
    colpresentation = ['input', 'input', 'input', 'input', 'input', 'markdown', 'input', 'input']

    dt_cols = [{'name': x, 'id': y, 'type': z, 'presentation': a} for x, y, z, a in
               zip(colnames, cols, coltype, colpresentation)]

    moneyformat = FormatTemplate.money(2)
    numformat = Format(precision=0, scheme=Scheme.fixed).group(True)

    dt_cols[3]['format'] = moneyformat
    dt_cols[4]['format'] = numformat

    return dt_cols


unicornsfilename = 'data/master_unicorns.xlsx'
master_unicorns = pd.read_excel(unicornsfilename)
master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)
unicornset = master_unicorns.loc[0:30,'Company Name']
unicorn_data = pd.read_pickle('data/unicorn_data')


layout = html.Div([

    dcc.Store(id='table-memory'),

    nb.gen_navbar(),

    html.Div(
        dt.DataTable(
            id='table1',
            columns=gen_table_format(),
            style_header={'fontWeight': 'bold', 'whiteSpace': 'normal', 'padding-left': '5px', 'padding-right': '5px'},
            style_cell={'textAlign': 'center'},
            sort_action='native',
        )
    )

])


