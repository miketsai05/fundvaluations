import dash_bootstrap_components as dbc
import dash_html_components as html

def gen_navbar():

    navbar = dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink("Summary", href='/apps/app_summary')),
        dbc.NavItem(dbc.NavLink("Company View", href='/apps/app_unicorn')),
        # dbc.NavItem(dbc.NavLink("Funds", href='/apps/app_fund')),
        # dbc.DropdownMenu(
        #     children=[
        #         dbc.DropdownMenuItem("Summary View", href='/apps/app_summary'),
        #         dbc.DropdownMenuItem("Individual View", href='/apps/app_unicorn'),
        #     ],
        #     nav=True,
        #     in_navbar=True,
        #     label='Unicorn Data',
        # ),
        dbc.NavItem(dbc.NavLink('Search Data', href='/apps/app_search')),
        dbc.NavItem(dbc.NavLink('About', href='/apps/app_about')),
        ],
        brand="SEC Reported Private Company Valuations",
        brand_style={'font-size': 32},
        brand_href="#",
        color="primary",
        dark=True,
        sticky='top',
        style={'font-size': 20}
    )

    return navbar


def gen_bottombar():

    footnote1 = 'Data automatically aggregated and provided “as is” without any representations or warranties, express or implied.'
    footnote2 = 'Not affiliated with the U.S. S.E.C. or EDGAR System.'
    footnote3 = 'Last updated as of September 13, 2021.'

    bbar = html.Div(
        [
            html.Hr(),
            html.P([footnote1, html.Br(), footnote2, html.Br(), footnote3]),
        ]
    )

    bottombar = dbc.Row(dbc.Col(bbar, width={'size': 10, 'offset': 1}))

    return bottombar