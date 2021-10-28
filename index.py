import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import app_about, app_summary, app_company, app_search


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def display_page(pathname):
    if pathname == '/apps/app_about':
        return app_about.layout
    elif pathname == '/apps/app_summary':
        return app_summary.layout
    elif pathname == '/apps/app_company':
        return app_company.layout
    elif pathname == '/apps/app_search':
        return app_search.layout
    else:
        return app_summary.layout


if __name__ == '__main__':
    app.run_server(debug=True)
