import pandas as pd
import plotly.express as px

def gen_fig(unicorn_name, selected_units):

    unicorn_data_grouped = pd.read_pickle('data/unicorn_data_grouped.pkl')
    unicorn_ind = unicorn_data_grouped['unicorn'] == unicorn_name
    unit_ind = unicorn_data_grouped['units'].isin(selected_units)
    gdata = unicorn_data_grouped[(unicorn_ind & unit_ind)].copy()

    return gen_fig_fromgdata(gdata, unicorn_name)


def gen_fig_fromgdata(gdata, graphtitle=''):
    gdata['valDatestr'] = gdata['valDate'].dt.strftime('%b %d, %Y')

    fig = px.scatter(gdata,
                     x='valDate',
                     y='pershare',
                     title=graphtitle,
                     size='normbalance',
                     color='fundManager',
                     template='simple_white',
                     hover_name='fundManager',
                     custom_data=['valDatestr', 'balance', 'seriesname']
                     )

    fig.update_layout(
            xaxis_title='Valuation Date',
            xaxis_tick0='1989-12-31',
            xaxis_dtick='M1',
            xaxis_tickformat='%b %d<br>%Y',
            yaxis_title='Per Share Valuation',
            yaxis_tickformat='$.2f',
            yaxis_rangemode='tozero',
            legend_title='Fund Manager',
            title={
                'x': 0.5,
                'y': 0.9,
                'xanchor': 'center',
                'yanchor': 'top',
                'font_family': 'Arial',
                'font_size': 28,
            }
    )

    fig.update_traces(
            #mode='lines+markers',
            #marker_symbol='square',
            #marker_opacity=1,
            opacity=0.6,
            hovertemplate=
                '<b>Fund Manager:</b> %{hovertext}<br>'
                '<b>Valuation Date:</b> %{customdata[0]}<br>'
                '<b>Per Share Valuation:</b> %{y:$0.2f}<br>'
                '<b>Aggregate Number of Shares:</b> %{customdata[1]:0,000}<br><br>'
                '<b>Held By:</b> <br>%{customdata[2]}'
                '<extra></extra>',
            hoverlabel=None
    )

    return fig
