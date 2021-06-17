#-

#TO DO add graph

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import pandas as pd
import select_data as sd
from apps.navbar import gen_navbar

from app import app


def gen_table(search_name):

    cols = ['fundManager', 'seriesname', 'valDate', 'pershare', 'balance', 'name', 'title', 'filingURL'] #don't need this in both functions
    tmptable = sd.search_select(search_name)
    tmptable = sd.merge_data(tmptable)

    tmptable = tmptable[cols]
    tmptable['Fund_xml'] = '['+tmptable['seriesname'].astype(str)+']('+tmptable['filingURL'].str[:-4]
    tmptable['Fund_xml'] = tmptable['Fund_xml'].str.replace('-', '')+'/xslFormNPORT-P_X01/primary_doc.xml)'
    tmptable['Fund_html']= '['+tmptable['seriesname'].astype(str)+']('+tmptable['filingURL'].astype(str)+')'
    tmptable['valDate'] = tmptable['valDate'].dt.date

    return tmptable


def gen_table_format():
    cols = ['fundManager', 'Fund_xml', 'valDate', 'pershare', 'balance',  'name', 'title']
    colnames = ['Fund Manager', 'Fund', 'Valuation Date', 'Per Share Valuation', 'Number of Shares',
                'Holding Name', 'Holding Title']
    coltype = ['text', 'text', 'datetime', 'numeric', 'numeric', 'text', 'text']
    colpresentation = ['input', 'markdown', 'input', 'input', 'input', 'input', 'input']

    dt_cols = [{'name': x, 'id': y, 'type': z, 'presentation': a} for x, y, z, a in
               zip(colnames, cols, coltype, colpresentation)]

    moneyformat = FormatTemplate.money(2)
    numformat = Format(precision=0, scheme=Scheme.fixed).group(True)

    dt_cols[3]['format'] = moneyformat
    dt_cols[4]['format'] = numformat

    return dt_cols


# external_stylesheets = [dbc.themes.LUMEN] # ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #SPACELAB, FLATLY
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# app.layout = html.Div([

#add note that only showing level 3 holdings. once public, shares indicaitons no longer presented

layout = html.Div([

    dcc.Store(id='table-memory2'),

    gen_navbar(),

    dbc.Row([
            dbc.Input(
                id="search-input2",
                placeholder="Search Level 3 holdings data from N-PORT filings for key word",
                type="search",
                style={'width': '30%', 'display': 'inline-block', 'padding-right': '10px'}),
            dbc.Button("Search", id="search-button2", className="mr-2", style={'display': 'inline-block'}),
        ],
        style={'padding-left': '30px', 'padding-bottom': '10px', 'padding-top': '40px'},
    ),

    dbc.Row(html.P(id='err', style={'color': 'red', 'textAlign': 'left'}),
            style={'padding-left': '30px'}),

    # html.Div(
    #     dcc.Graph(
    #         id='valuations-graph'
    #     ),
    #     style={'width': '79%', 'display': 'inline-block', 'vertical-align': 'top'}
    # ),

    dbc.Row([
        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterManager2',
                    options=[],
                    value=[]),
                label='Filter Table by Fund Manager',),
            style={'width': 'auto', 'display': 'inline-block', 'padding-left': '30px', 'padding-right': '10px'}),

        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterDate2',
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
        #         id="link-input2"),
        #     style={'display':'inline-block', 'padding-left': '20px'}),

        ],
        style={'padding-bottom': '10px'}
    ),

    html.Div(
        dt.DataTable(
            id='table2',
            columns=gen_table_format(),
            style_header={'fontWeight': 'bold', 'whiteSpace': 'normal', 'padding-left': '5px', 'padding-right': '5px'},
            style_cell={'textAlign': 'center', 'font-family': 'sans-serif', 'whiteSpace': 'normal'},
            sort_action='native',
        )
    )

])


# add toggle to change size of points on graph

@app.callback(
    Output(component_id='table-memory2', component_property='data'),
    Output(component_id='filterManager2', component_property='options'),
    Output(component_id='filterManager2', component_property='value'),
    Output(component_id='filterDate2', component_property='options'),
    Output(component_id='filterDate2', component_property='value'),
    Output(component_id='err', component_property='children'),
    Input(component_id='search-button2', component_property='n_clicks'),
    Input(component_id='search-input2', component_property='n_submit'),
    State(component_id='search-input2', component_property='value'),
)
def update_graph(n_clicks, n_submit, input_value):
    if input_value is None:
        raise dash.exceptions.PreventUpdate
    if len(input_value) <= 3:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Please enter at least 3 characters'
    else:
        tmptable = gen_table(input_value)
        if len(tmptable) == 0:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'No data matching key word found'
        else:
            manageroptions = [{'label': i, 'value': i} for i in sorted(tmptable['fundManager'].astype(str).unique())]
            managerval = sorted(tmptable['fundManager'].astype(str).unique())
            dateoptions = [{'label': i, 'value': i} for i in sorted(tmptable['valDate'].unique(), reverse=True)]
            dateval = sorted(tmptable['valDate'].unique(), reverse=True)
            return tmptable.to_dict('records'), manageroptions, managerval, dateoptions, dateval, ''
    # return sd.gen_fig(input_value), tmptable.to_dict('records'), manageroptions, managerval, dateoptions, dateval


@app.callback(
    Output(component_id='table2', component_property='data'),
    Input(component_id='filterManager2', component_property='value'),
    Input(component_id='filterDate2', component_property='value'),
    Input(component_id='table-memory2', component_property='data')
)
def filter_table(selectmanager, selectdate, data):
    tmptable = pd.DataFrame.from_dict(data)
    tmptable = tmptable[tmptable['fundManager'].isin(selectmanager) & tmptable['valDate'].isin(selectdate)]
    return tmptable.to_dict('records')
