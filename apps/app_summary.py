#TO DO - ADD AVERAGE PRICE WITHIN QUARTER
#TO DO show type of investments
#TO DO trend?? - # marking up, # marking down - sort by biggest options, YoY, QoQ, MoM
#TO DO valuationdate - make one line

#TO DO link each unicorn to individual page
#TO DO replace ravel with another function

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import pandas as pd
import apps.navbar as nb

from app import app


def gen_summary_data():


    tmptable1 = pd.read_pickle('data/unicorn_summary.pkl')
    tmptable1['unicornlink'] = '['+tmptable1['unicorn'].astype(str)+'](/apps/app_unicorn#'+tmptable1['unicorn'].str.replace(' ', '_').astype(str)+')'

    # types of investments, trend, average price within quarter

    return tmptable1


def gen_table_format():

    cols = ['unicornlink', 'Country', 'Industry', 'fundManagerunique', 'accessNumcount',
            'valDatemin', 'valDatemax',
            'increase', 'flat', 'decrease']
    colheader = ['', '', '', '', '',
                 'Valuation Dates Available', 'Valuation Dates Available',
                 'Most Recent Quarter Valuation Changes', 'Most Recent Quarter Valuation Changes', 'Most Recent Quarter Valuation Changes' ]
    colnames = ['Company', 'Country', 'Industry', 'Fund Managers', 'Total Filings',
                'From', 'To',
                'Increased', 'Flat', 'Decreased']
    coltype = ['text', 'text', 'text', 'text', 'numeric',
               'text', 'text',
               'text', 'text', 'text']
    colpresentation = ['markdown', 'input', 'input', 'input', 'input',
                       'input', 'input',
                       'input', 'input', 'input']

    dt_cols = [{'name': [w, x], 'id': y, 'type': z, 'presentation': a} for w, x, y, z, a in
               zip(colheader, colnames, cols, coltype, colpresentation)]

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
            merge_duplicate_headers=True,
            style_header={
                'fontWeight': 'bold',
                'whiteSpace': 'normal',
                'padding-left': '5px',
                'padding-right': '5px'
            },
            style_cell={
                'textAlign': 'center',
                'lineHeight': '15px',
                'font-family': 'sans-serif',
                'whiteSpace': 'nowrap',
            },
            style_data={
                'height': 'auto',
                'lineHeight': '15px',
            },
            style_cell_conditional=[
                {'if': {'column_id': c},
                    'height': 'auto',
                    'whiteSpace': 'normal',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'}
                for c in ['fundManagerunique', 'Industry']
            ],
            style_data_conditional=[{'if': {'column_id': 'unicornlink'}, 'padding-top': 15}],
            sort_action='native',
            markdown_options={'link_target': '_self'}
        ),
        style={'padding-top': '20px'}
    ),

    nb.gen_bottombar()

])


