import dash_bootstrap_components as dbc
import dash_html_components as html

def gen_navbar():

    navbar = dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink("Home", href='/apps/app_home')),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Summary List", href='/apps/app_summary'),
                dbc.DropdownMenuItem("Individual", href='/apps/app_unicorn'),
            ],
            nav=True,
            in_navbar=True,
            label='Unicorns',
        ),
        dbc.NavItem(dbc.NavLink('Search All', href='/apps/app_search'))
        ],
        brand="SEC Reported Valuations",
        brand_style={'font-size': 32},
        brand_href="#",
        color="primary",
        dark=True,
        sticky='top',
        style={'font-size': 18}
    )

    return navbar


def gen_bottombar():

    footnote1 = 'Data is automatically aggregated and provided “as is” without any representations or warranties, express or implied.'
    footnote2 = 'Not affiliated with the U.S. S.E.C. or EDGAR System.'

    bbar = html.Div(
        [
            html.Hr(),
            html.P([footnote1, html.Br(), footnote2]),
        ]
    )

    bottombar = dbc.Row(dbc.Col(bbar, width={'size': 10, 'offset': 1}))

    return bottombar