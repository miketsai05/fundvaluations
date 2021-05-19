import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app_home, app_summary, app_unicorn, app_search


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/app_home':
        return app_home.layout
    elif pathname == '/apps/app_summary':
        return app_summary.layout
    elif pathname == '/apps/app_unicorn':
        return app_unicorn.layout
    elif pathname == '/apps/app_search':
        return app_search.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
