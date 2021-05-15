#need to add code for case of no records returned
#show debt as separate table as percentage of par split based on NS vs PA

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

    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Summary List", href='#'),
                dbc.DropdownMenuItem("Individual", href='/apps/app_unicorn'),
            ],
            nav=True,
            in_navbar=True,
            label='Unicorns',
        ),
        dbc.NavItem(dbc.NavLink('Search All',href='/apps/app_search'))
        ],
        brand="SEC Reported Valuations",
        brand_style={'font-size': 32},
        brand_href="#",
        color="primary",
        dark=True,
        sticky='top',
        style={'font-size': 18}
    ),

    html.Div([
        html.Label('Company Name'),
        dcc.Dropdown(
            id='company-input',
            options=[{'label': x, 'value': x} for x in unicornset],
            value='Bytedance',
            clearable=False
        )
        ],
        style={'padding-top': '5%', 'padding-left': '10px', 'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

    html.Div(
        dcc.Graph(
            id='valuations-graph'
        ),
        style={'width': '79%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

    dbc.Row([
        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterManager',
                    options=[],
                    value=[],
                ),
                label='Filter Table by Fund Manager',
            ),
            style={'width': 'auto', 'display': 'inline-block', 'padding-left': '30px', 'padding-right': '10px'}
        ),

        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterDate',
                    options=[],
                    value=[],
                ),
                label='Filter Table by Valuation Date',
            ),
            style={'width': 'auto', 'display': 'inline-block'}
        ),

        html.Div(
            dbc.RadioItems(
                options=[
                    {"label": "Link to html filings", "value": 1},
                    {"label": "Link to text filings", "value": 2},
                ],
                value=1,
                id="link-input",
            ),
            style={'display':'inline-block', 'padding-left': '20px'}
        ),
        ],
    style={'padding-bottom': '10px'}
    ),

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


# add toggle to change size of points on graph

@app.callback(
    Output(component_id='valuations-graph', component_property='figure'),
    Output(component_id='table-memory', component_property='data'),
    Output(component_id='filterManager', component_property='options'),
    Output(component_id='filterManager', component_property='value'),
    Output(component_id='filterDate', component_property='options'),
    Output(component_id='filterDate', component_property='value'),
    Input(component_id='company-input', component_property='value')
)
def update_graph(input_value):
    tmptable = gen_table(input_value)
    manageroptions = [{'label': i, 'value': i} for i in sorted(tmptable['fundManager'].unique())]
    managerval = sorted(tmptable['fundManager'].unique())
    dateoptions = [{'label': i, 'value': i} for i in sorted(tmptable['valDate'].unique(), reverse=True)]
    dateval = sorted(tmptable['valDate'].unique(), reverse=True)
    return sd.gen_fig(input_value), tmptable.to_dict('records'), manageroptions, managerval, dateoptions, dateval


@app.callback(
    Output(component_id='table1', component_property='data'),
    Input(component_id='filterManager', component_property='value'),
    Input(component_id='filterDate', component_property='value'),
    Input(component_id='table-memory', component_property='data')
)
def filter_table(selectmanager, selectdate, data):
    tmptable = pd.DataFrame.from_dict(data)
    tmptable = tmptable[tmptable['fundManager'].isin(selectmanager) & tmptable['valDate'].isin(selectdate)]
    return tmptable.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)