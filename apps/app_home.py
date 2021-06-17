#largest quarter-o-Q change, biggest divergence
#add a fund page? that lists holdings? grouped and collapsable?

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import pandas as pd
import select_data as sd
import apps.navbar as nb

from app import app


tmptext = '1Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.'
sec_imgname = 'sec-logo.png'

def gen_thumbnail(imgname, url, fund):
    return html.Div(
        html.A(
            html.Img(
                src = app.get_asset_url(imgname),
                style = {
                    # 'object-fit': 'contain', # HOW TO GET THIS TO WORK?
                    'max-height': '50px',
                    'max-width': '160px',
                    'width': 'auto',
                    'height': 'auto',
                    'float': 'left',
                    'position': 'relative',
                    'padding-bottom': 5,
                    'padding-right': 0
                }
            ),
            href=url,
            target='_blank'
        ),
    )

def gen_thumbnail2(imgname, url, fund):
    return dbc.Row(
        dbc.Col(
            html.A(
                html.Img(
                    src = app.get_asset_url(imgname),
                    style = {
                        'width': '160px',
                        'height': '50px',
                        'object-fit': 'contain',  # HOW TO GET THIS TO WORK?
                        # 'max-height': '50px',
                        # 'max-width': '160px',
                        # 'width': 'auto',
                        # 'height': 'auto',
                        'float': 'none',
                        'position': 'static',
                        'padding-bottom': 5,
                        # 'border': '1px solid black'
                    }
                ),
                href=url,
                target='_blank'
            ),
            style={'textAlign': 'center'})
    )


master_funds = pd.read_excel('data/master_funds.xlsx', sheet_name='fund_details')
images_div = []
for i in range(master_funds.shape[0]):
    images_div.append(gen_thumbnail2(master_funds.logo[i], master_funds.url[i], master_funds.fund[i]))

layout = html.Div([

    nb.gen_navbar(),

    dbc.Container([

        dbc.Row([

            dbc.Col([

                dbc.Row(
                    dbc.Col(
                        html.Img(
                            src=app.get_asset_url(sec_imgname),
                            style={'width': 'auto', 'height': 'auto'}),
                        style={'padding-bottom': '20px', 'textAlign': 'center'}),
                ),

                dbc.Row(
                    dbc.Col(
                        html.Label('Valuations from over 2000+ mutual funds including:'),
                        style={'verticalAlign': 'center', 'font-size': 12})
                ),

                dbc.Row(
                    dbc.Col(
                        images_div,
                        style={}))],

                width=2,
                style={'padding-bottom': '30px', 'textAlign': 'center'}
            ),

            dbc.Col(
                html.Div([
                    html.P(dcc.Markdown('''  
    ## Overview
    
    Private equity markets have changed dramatically in recent years with firms staying private longer than ever.
    Alongside this shift has been an increasing trend of pre-IPO participation by crossover investors including  
    many mutual funds. 
    
    Although there is no definitive data source for the tick by tick valuation of a private company 
    as there are for public markets, mutual fund valuations provide one of the few observable data points the public 
    can reference to provide an indication of what these private company shares are valued at. 
    
    This project is intended to help aggregate, visualize and surface Level 3 fair values reported in SEC 
    N-PORT filing data starting September 30, 2019. 
    
    ## What is Form N-PORT?
    
    In October 2016, the SEC adopted the Investment Company Reporting Modernization rule, introducing Form N-PORT 
    to replace the previously required Form N-Q. Form N-PORT requires funds to report complete portfolio holdings 
    details on a position by position basis. Registered Investment Companies (RICs) must submit monthly N-PORT 
    reports although only the fiscal quarter end N-PORT reports are made available to the public
    
    The compliance timeline for larger fund groups began with quarter ending March 31, 2019 and for smaller fund 
    groups began with quarter ending March 31, 2020. However, the first 6 months of N-PORT filings were kept private
    so the first publicly available N-PORT filings begin with quarter ending September 30, 2019. The submission 
    deadlines are 60 days after each fiscal quarter end.
    
    ## Why only Form N-PORT?
    
    Prior to the Investment Company Reporting Modernization rule, mutual funds were required to submit Form N-Q.
    There were a number of key changes from the prior Form N-Q to the current Form N-PORT that make the 
    reported data in Form N-PORT easier to work with including:
    * Form N-PORT reports are submitted in XML format instead of HTML format
    * Form N-PORT expands the scope of required level of detail much of which was not previously required with Form N-Q
    * Form N-PORT are publicly available on a quarterly basis whereas Form N-Q was only required semi-annually
    
    ## What are Level 3 fair values?
    
    Accounting standards ASC 820 and IFRS 13 establish an authoritative definition of fair value and sets out a 
    hierarchy for measuring fair value that can be summarized as follows:
    * Level 1: Fair value based on quoted prices in active markets for identical securities.
    * Level 2: Fair value based on observable inputs either directly or indirectly.
    * Level 3: Fair value based on unobservable inputs.
    
    There are many readily available sources for Level 1 and Level 2 valuations so this project seeks to focus on only
    Level 3 valuations.
    
    ## Additional Information:
    * [Investment Company Reporting Modernization Summary][1]
    * [Investment Company Reporting Modernization Full Rule][2]
    * [Investment Company Reporting Modernization FAQ][3]
    
    [1]: https://www.sec.gov/divisions/investment/guidance/secg-investment-company-reporting-modernization-rules.htm
    [2]: https://www.sec.gov/rules/final/2016/33-10231.pdf
    [3]: https://www.sec.gov/investment/investment-company-reporting-modernization-faq
    
                    ''')),
                ]),
                width=7),

            dbc.Col([
                dbc.Row(html.Div(tmptext)),
                dbc.Row(html.Div(tmptext))],
                width=3),
        ],
        style={'padding-top': '20px'}),

        nb.gen_bottombar()])

    ])
