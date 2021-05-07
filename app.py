# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import selectData as sd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

# fig = px.scatter(df, x="gdp per capita", y="life expectancy",
#                  size="population", color="continent", hover_name="country",
#                  log_x=True, size_max=60)

fig = sd.gen_fig('Bytedance')

unicornsfilename = 'master_unicorns.xlsx'
master_unicorns = pd.read_excel(unicornsfilename)
master_unicorns = master_unicorns.where(pd.notnull(master_unicorns), None)
uni_list = [{'label': x, 'value': x} for x in master_unicorns.loc[0:30,'Company Name']]

app.layout = html.Div([

    html.H1(
        'SEC Reported Valuations',
        style={'textAlign': 'center'}
    ),

    html.Div([
        html.Label('Company Name'),
        dcc.Dropdown(
            id='company-input',
            options=[{'label': x, 'value': x} for x in master_unicorns.loc[0:30,'Company Name']],
            value='Bytedance')]
    ,style={'padding-top': '5%', 'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div(
        dcc.Graph(
            id='valuations-graph',
            figure=fig
        )
    ,style={'width': '79%', 'display': 'inline-block', 'vertical-align': 'top'}),


])

# add toggle to change size of points on graph

@app.callback(
    Output(component_id='valuations-graph', component_property='figure'),
    Input(component_id='company-input', component_property='value')
)
def update_graph(input_value):
    return sd.gen_fig(input_value)


if __name__ == '__main__':
    app.run_server(debug=True)