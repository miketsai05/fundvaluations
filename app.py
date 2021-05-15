import dash
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.LUMEN] # ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #SPACELAB, FLATLY
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
server = app.server