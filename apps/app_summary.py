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
    tmptable1['unicornlink'] = '['+tmptable1['unicorn'].astype(str)+'](/apps/app_company#'+tmptable1['unicorn'].str.replace(' ', '_').astype(str)+')'

    # types of investments, trend, average price within quarter

    return tmptable1


def gen_table_format():

    cols = ['unicornlink', 'fundManagerunique',
            'persharemean', 'persharerange', 'QoQpercentdiffmean',
            'increase', 'decrease',  'quarterfilingcount',
            'valDatemin', 'valDatemax']
    colheader = ['', '',
                 'Most Recent Quarter Valuations (Per Share)', 'Most Recent Quarter Valuations (Per Share)', 'Most Recent Quarter Valuations (Per Share)',
                 'Most Recent Quarter Valuations (Per Share)', 'Most Recent Quarter Valuations (Per Share)', 'Most Recent Quarter Valuations (Per Share)',
                 'Valuation Dates Available', 'Valuation Dates Available']
    colnames = ['Company', 'Mutual Fund Investors',
                'Average Price', 'Price Range', '% Change (Average)',
                'Increases', 'Decreases', 'Filings',
                'From', 'To']
    coltype = ['text', 'text',
               'numeric', 'text', 'numeric',
               'text', 'text', 'text',
               'text', 'text']
    colpresentation = ['markdown', 'input',
                       'input', 'input', 'input',
                       'input', 'input', 'input',
                       'input', 'input']

    dt_cols = [{'name': [w, x], 'id': y, 'type': z, 'presentation': a} for w, x, y, z, a in
               zip(colheader, colnames, cols, coltype, colpresentation)]

    # countformat = Format(precision=0, scheme=Scheme.fixed).group(True)
    #
    # dt_cols[3]['format'] = countformat
    dt_cols[2]['format'] = FormatTemplate.money(2)
    dt_cols[4]['format'] = FormatTemplate.percentage(1)

    return dt_cols


layout = html.Div([

    nb.gen_navbar(),

    dbc.Container(

        dt.DataTable(
            id='table1',
            data = gen_summary_data().to_dict('records'),
            columns=gen_table_format(),
            merge_duplicate_headers=True,
            style_header={
                'fontWeight': 'bold',
                'whiteSpace': 'normal',
                'padding-left': '5px',
                'padding-right': '5px',
                'textAlign': 'center'
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
            style_header_conditional=[
                {'if': {'column_id': c},
                    'textAlign': 'left'}
                for c in ['unicornlink', 'fundManagerunique']
            ],
            style_cell_conditional=[
                {'if': {'column_id': c},
                    'whiteSpace': 'normal',
                    'textAlign': 'left'}
                    # 'line-height': '15px',
                    # 'max-height': '30px',
                    # 'min-height': '30px',
                    # 'height': '30px',
                    # 'overflow-y': 'hidden',
                    # 'display': 'block'}
                for c in ['fundManagerunique']
            ],
            style_data_conditional=[{'if': {'column_id': 'unicornlink'}, 'padding-top': 15}],
            tooltip_data=[{'fundManagerunique': x} for x in gen_summary_data()['fundManagerunique']],
            tooltip_duration=None,
            css=[{
                'selector': '.dash-spreadsheet td div',
                'rule': '''
                            line-height: 15px;
                            max-height: 30px; min-height: 30px; height: 30px;
                            display: block;
                            overflow-y: hidden;
                        '''
            }],
            sort_action='native',
            markdown_options={'link_target': '_self'}
        ),
        style={'padding-top': '20px'}
    ),

    nb.gen_bottombar()

])


