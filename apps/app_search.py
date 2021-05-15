#need to add code for case of no records returned
#show debt as separate table as percentage of par split based on NS vs PA

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

from app import app

def gen_table(search_name):
    cols = ['fundManager', 'valDate', 'pershare', 'balance', 'Fund', 'name', 'title', 'filingURL'] #don't need this in both functions
    tmptable = sd.search_select(search_name)
    tmptable = sd.merge_data(tmptable)
    tmptable = tmptable[cols]
    tmptable['Fund_xml'] = '['+tmptable['Fund'].astype(str)+']('+tmptable['filingURL'].str[:-24]+'xslFormNPORT-P_X01/primary_doc.xml)'
    tmptable['Fund_html']= '['+tmptable['Fund'].astype(str)+']('+tmptable['filingURL'].astype(str)+')'
    tmptable['valDate'] = tmptable['valDate'].dt.date
    return tmptable


def gen_table_format():
    cols = ['fundManager', 'valDate', 'pershare', 'balance', 'Fund_xml', 'name', 'title']
    colnames = ['Fund Manager', 'Valuation Date', 'Per Share Valuation', 'Number of Shares', 'Fund',
                'Holding Name', 'Holding Title']
    coltype = ['text', 'datetime', 'numeric', 'numeric', 'text', 'text', 'text']
    colpresentation = ['input', 'input', 'input', 'input', 'markdown', 'input', 'input']

    dt_cols = [{'name': x, 'id': y, 'type': z, 'presentation': a} for x, y, z, a in
               zip(colnames, cols, coltype, colpresentation)]

    moneyformat = FormatTemplate.money(2)
    numformat = Format(precision=0, scheme=Scheme.fixed).group(True)

    dt_cols[2]['format'] = moneyformat
    dt_cols[3]['format'] = numformat

    return dt_cols


# external_stylesheets = [dbc.themes.LUMEN] # ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #SPACELAB, FLATLY
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# app.layout = html.Div([

layout = html.Div([

    dcc.Store(id='table-memory2'),

    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Summary List", href="#"),
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

    dbc.Row(
        [
            dbc.Input(
                id="search-input2",
                placeholder="Search all mutual fund valuations...3",
                type="search",
                style={'width': '30%', 'display': 'inline-block', 'padding-right': '10px'},
                # debounce=True
            ),
            dbc.Button("Search", id="search-button2", className="mr-2", style={'display': 'inline-block'}),
        ],
        style={'padding-left': '30px', 'padding-bottom': '20px', 'padding-top': '40px'},
    ),

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
                    value=[],
                ),
                label='Filter Table by Fund Manager',
            ),
            style={'width': 'auto', 'display': 'inline-block', 'padding-left': '30px', 'padding-right': '10px'}
        ),

        html.Div(
            dbc.DropdownMenu(
                dbc.Checklist(
                    id='filterDate2',
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
                id="link-input2",
            ),
            style={'display':'inline-block', 'padding-left': '20px'}
        ),
        ],
    style={'padding-bottom': '10px'}
    ),

    html.Div(
        dt.DataTable(
            id='table2',
            columns=gen_table_format(),
            style_header={'fontWeight': 'bold', 'whiteSpace': 'normal', 'padding-left': '5px', 'padding-right': '5px'},
            style_cell={'textAlign': 'center'},
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
    Input(component_id='search-button2', component_property='n_clicks'),
    Input(component_id='search-input2', component_property='n_submit'),
    State(component_id='search-input2', component_property='value'),
)
def update_graph(n_clicks, n_submit, input_value):
    if input_value is None:
        raise dash.exceptions.PreventUpdate
    if len(input_value) <=3:
        return dash.no_update, 'Please enter at least 3 characters'
    else:
        tmptable = gen_table(input_value)
        manageroptions = [{'label': i, 'value': i} for i in sorted(tmptable['fundManager'].unique())]
        managerval = sorted(tmptable['fundManager'].unique())
        dateoptions = [{'label': i, 'value': i} for i in sorted(tmptable['valDate'].unique(), reverse=True)]
        dateval = sorted(tmptable['valDate'].unique(), reverse=True)
        return tmptable.to_dict('records'), manageroptions, managerval, dateoptions, dateval
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


if __name__ == '__main__':
    app.run_server(debug=True)