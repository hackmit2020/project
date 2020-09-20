import dash
import dash_html_components as html
import dash_core_components as dcc

import os
import pathlib
import re

import pandas as pd
from dash.dependencies import Input, Output, State
#import cufflinks as cf


import plotly.express as px
from datetime import datetime
from urllib.request import urlopen
import json

from data.jhcovid.jh import JHCovid

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "data/")

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

external_stylesheets = ['styles.css']

with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    states = json.load(response)


MONTHS = ['FEB', 'MAR', 'APR', 'MAY', 'JUN','JUL','AUG','SEP']
MONTHS_NUM = [2,3,4,5,6,7,8,9]

DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#bbffeb",
    "#98ffe0",
    "#79ffd6",
    "#6df0c8",
    "#69e7c0",
    "#59dab2",
    "#45d0a5",
    "#31c194",
    "#2bb489",
    "#25a27b",
    "#1e906d",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]

slider_marks = dict(zip(MONTHS_NUM,MONTHS))

jh = JHCovid()
df_month = jh.get()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='my-slider',
        min=2,
        max=9,
        step=None,
        marks=slider_marks,
        value=2
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('my-slider', 'value')])
def update_figure(selected_month):
    #nov_mask = df_month['Dates'].map(lambda x: x.month) == 11
    filtered_df = df_month[df_month['Date'].map(lambda x: x.month) == selected_month]
    #filtered_df = df[df.year == selected_month]

    print(filtered_df)

    fig = px.choropleth_mapbox(filtered_df, geojson=states, locations='FIPS', color='Confirmed',
                               color_continuous_scale=DEFAULT_COLORSCALE, range_color=(0, 20000),
                               mapbox_style="carto-positron", zoom=2, center={"lat": 37.0902, "lon": -95.7129},
                               hover_name='Confirmed')

    # fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
    #                  size="pop", color="continent", hover_name="country",
    #                  log_x=True, size_max=55)

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

'''
MONTHS = ['FEB', 'MAR', 'APR', 'MAY', 'JUN','JUL','AUG','SEP']
MONTHS_NUM = [2,3,4,5,6,7,8,9]

slider_marks = dict(zip(MONTHS_NUM,MONTHS))
print(slider_marks)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Slider(
        id='my-slider',
        min=2,
        max=9,
        step=None,
        marks=slider_marks,
        value=2
    ),
    html.Div(id='slider-output-container')
])

# Load COVID data
with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    states = json.load(response)

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "data/")

df = JHCovid().get()
print(df['Confirmed'])


@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])


def update_output(value):
    return 'You have selected "{}"'.format(slider_marks[value])



if __name__ == '__main__':
    app.run_server(debug=True)
'''
