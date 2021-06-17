


#TO DO add specific colors per fundmanager


#TO DO callback to change sec link from html to txt (maybe add hover to explain)
#TO DO show debt as separate table as percentage of par split based on NS vs PA
#TO DO add toggle to change size of points on graph

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import select_data as sd
from apps.navbar import gen_navbar

from app import app


def gen_table(unicorn_name, selected_units):

    cols = ['unicorn', 'fundManager', 'seriesname', 'valDate', 'pershare', 'balance', 'name', 'title', 'filingURL'] #don't need this in both functions
    unicorn_ind = unicorn_data['unicorn'] == unicorn_name
    unit_ind = unicorn_data['units'].isin(selected_units)
    tmptable = unicorn_data[ (unicorn_ind & unit_ind) ][cols].copy()
    tmptable['Fund_xml'] = '['+tmptable['seriesname'].astype(str)+']('+tmptable['filingURL'].str[:-4]
    tmptable['Fund_xml'] = tmptable['Fund_xml'].str.replace('-', '')+'/xslFormNPORT-P_X01/primary_doc.xml)'
    tmptable['Fund_html']= '['+tmptable['seriesname'].astype(str)+']('+tmptable['filingURL'].astype(str)+')'
    tmptable['valDate'] = tmptable['valDate'].dt.date

    available_units = list(set(unicorn_data[unicorn_ind]['units']))

    return tmptable, available_units


def gen_table_format():

    cols = ['unicorn', 'fundManager', 'Fund_xml', 'valDate', 'pershare', 'balance', 'name', 'title']
    colnames = ['Company', 'Fund Manager', 'Fund', 'Valuation Date', 'Per Share Valuation', 'Number of Shares',
                'Holding Name', 'Holding Title']
    coltype = ['text', 'text', 'text', 'datetime', 'numeric', 'numeric', 'text', 'text']
    colpresentation = ['input', 'input', 'markdown', 'input', 'input', 'input', 'input', 'input']

    dt_cols = [{'name': x, 'id': y, 'type': z, 'presentation': a} for x, y, z, a in
               zip(colnames, cols, coltype, colpresentation)]

    moneyformat = FormatTemplate.money(2)
    numformat = Format(precision=0, scheme=Scheme.fixed).group(True)

    dt_cols[4]['format'] = moneyformat
    dt_cols[5]['format'] = numformat

    return dt_cols


unicornsfilename = 'data/master_unicorns.xlsx'
master_unicorns = pd.read_excel(unicornsfilename)
master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)
unicornset = master_unicorns.loc[0:30,'Company Name']
unicorn_data = pd.read_pickle('data/unicorn_data.pkl')
havedata = set(unicorn_data['unicorn'].str.lower())


layout = html.Div([

    dcc.Store(id='table-memory'),

    gen_navbar(),

    html.Div([
        html.Label('Company Name'),
        dcc.Dropdown(
            id='company-input',
            options=[{'label': x, 'value': x} for x in unicornset if x.lower() in havedata],
            value='Bytedance',
            clearable=False),
        dbc.Label('Asset Type', style={'padding-top': '15px'}),
        dbc.Checklist(
            options=[
                {'label': 'Equity', 'value': 'NS'},
                {'label': 'Debt', 'value': 'PA'},
                {'label': 'Derivatives', 'value': 'NC', 'disabled': True},
                {'label': 'Other', 'value': 'OU', 'disabled': True}
            ],
            value=['NS'],
            id='unitType',
            switch=True
        )],
        style={'padding-top': '5%', 'padding-left': '10px', 'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

    html.Div(
        dcc.Graph(id='valuations-graph'),
        style={'width': '79%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

    dbc.Row([
        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterManager',
                    options=[],
                    value=[],),
                label='Filter Table by Fund Manager',),
            style={'width': 'auto', 'display': 'inline-block', 'padding-left': '30px', 'padding-right': '10px'}),

        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterDate',
                    options=[],
                    value=[],),
                label='Filter Table by Valuation Date',),
            style={'width': 'auto', 'display': 'inline-block'}),

        # html.Div(
        #     dbc.RadioItems(
        #         options=[
        #             {"label": "Link to html filings", "value": 1},
        #             {"label": "Link to text filings", "value": 2},
        #         ],
        #         value=1,
        #         id="link-input",),
        #     style={'display': 'inline-block', 'padding-left': '20px'})
        ],
        style={'padding-bottom': '10px'}
    ),

    html.Div(
        dt.DataTable(
            id='table1',
            columns=gen_table_format(),
            style_header={'fontWeight': 'bold', 'whiteSpace': 'normal', 'padding-left': '5px', 'padding-right': '5px'},
            style_cell={'textAlign': 'center'},
            sort_action='native',)
    )

])




@app.callback(
    Output(component_id='valuations-graph', component_property='figure'),
    Output(component_id='table-memory', component_property='data'),
    Output(component_id='filterManager', component_property='options'),
    Output(component_id='filterManager', component_property='value'),
    Output(component_id='filterDate', component_property='options'),
    Output(component_id='filterDate', component_property='value'),
    Output(component_id='unitType', component_property='options'),
    Input(component_id='company-input', component_property='value'),
    Input(component_id='unitType', component_property='value')
)
def update_graph(input_value, selected_units):
    if len(selected_units) == 0:
        selected_units = ['NS']
    tmptable, available_units = gen_table(input_value, selected_units)

    lunit = ['Equity', 'Debt', 'Derivatives', 'Other']
    vunit = ['NS', 'PA', 'NC', 'OU']
    dunit = [x not in available_units for x in vunit]
    unitoptions = [{'label': l, 'value': v, 'disabled': d} for l, v, d in zip(lunit, vunit, dunit)]

    manageroptions = [{'label': i, 'value': i} for i in sorted(tmptable['fundManager'].astype(str).unique())]
    managerval = sorted(tmptable['fundManager'].astype(str).unique())

    dateoptions = [{'label': i, 'value': i} for i in sorted(tmptable['valDate'].unique(), reverse=True)]
    dateval = sorted(tmptable['valDate'].unique(), reverse=True)

    outfig = sd.gen_fig(input_value, selected_units)

    return outfig, tmptable.to_dict('records'), manageroptions, managerval, dateoptions, dateval, unitoptions


# @app.callback(
#     Output(component_id='valuations-graph', component_property='figure'),
#     Output(component_id='table-memory', component_property='data'),
#     Output(component_id='filterManager', component_property='options'),
#     Output(component_id='filterManager', component_property='value'),
#     Output(component_id='filterDate', component_property='options'),
#     Output(component_id='filterDate', component_property='value'),
#     Output(component_id='unitType', component_property='options'),
#     Output(component_id='unitType', component_property='value'),
#     Input(component_id='unitType', component_property='value')
# )



@app.callback(
    Output(component_id='table1', component_property='data'),
    Input(component_id='filterManager', component_property='value'),
    Input(component_id='filterDate', component_property='value'),
    Input(component_id='table-memory', component_property='data'),
    prevent_initial_call=True
)
def filter_table(selectmanager, selectdate, data):
    tmptable = pd.DataFrame.from_dict(data)
    tmptable = tmptable[tmptable['fundManager'].isin(selectmanager) & tmptable['valDate'].isin(selectdate)]
    return tmptable.to_dict('records')
