#add explanation for NPORTP - structured xml, easy to parse
#explain valuations, triangulation, support details, fair value - asc820/ifrs 13
#purpose of page, help visualize, small attempt to help improve transparency
#largest quarter-o-Q change, biggest divergence
#list mutual funds logos

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
imgpath = 'sec-logo.png'

layout = html.Div([

    nb.gen_navbar(),

    dbc.Container([

        dbc.Row([

            dbc.Col(html.Img(src=app.get_asset_url(imgpath)), width=2),

            dbc.Col(
                html.Div([
                    html.P(dcc.Markdown('''
    # SEC Reported Valuations
    
    
    ## Overview
    
    Private equity markets have changed dramatically in recent years with firms staying private longer than ever.
    Alongside this shift has been an increasing trend of pre-IPO participation by crossover investors including  
    many mutual funds. 
    
    Although there is no definitive data source for the tick by tick valuation of a private company 
    as there are for public markets, mutual fund valuations are one of the few observable data points the public 
    has that can provide an indication to what these private company’s shares are valued at. 
    
    This project is intended to help aggregate, visualize and surface reported Level 3 Fair Values from SEC 
    N-PORT filing data starting September 30, 2019. 
    
    ## What is Form N-PORT?
    
    In October 2016, the SEC adopted the Investment Company Reporting Modernization rule, introducing Form N-PORT 
    to replace the previously required Form N-Q. Form N-PORT requires funds to report complete portfolio holdings 
    details on a position by position basis. Registered Investment Companies (RICs) must submit monthly N-PORT 
    reports although only the fiscal quarter end N-PORT reports are made available to the public
    
    The compliance timeline for larger fund groups began with quarter ending Mar 31, 2019 and for smaller fund 
    groups began with quarter ending Mar 31, 2020. However, the first 6 months of N-PORT filings were kept private
    so the first publicly available filing begins with quarter ending sep 30, 2019. The submission deadlines are 
    60 days after each fiscal quarter end.
    
    ## Why only Form 'N-PORT'?
    
    Prior to the Investment Company Reporting Modernization rule, mutual funds were required to submit Form N-Q.
    Key changes between the Form N-PORT form and the prior Form N-Q include:
    * Form N-PORT reports are submitted in XML format instead of HTML format
    * Form N-PORT expands the score of required level of detail much of which was not previously required with Form N-Q
    * Form N-PORT are publicly available on a quarterly basis whereas Form N-Q was only required semi-annually
    Collectively, these changes makes date collection and analytics much easier.
    
    ## What are Level 3 Valuations?
    
    ## Additional information:
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
