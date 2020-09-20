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
from datetime import datetime, timedelta
from urllib.request import urlopen
import json

from data.jhcovid.jh import JHCovid
from data.nytimes import NYTQuery

nytimes = NYTQuery()
articles = nytimes.get()

state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California",
               "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida",
               "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas",
               "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan",
               "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina",
               "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico",
               "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
               "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
               "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington",
               "Wisconsin", "West Virginia", "Wyoming"]

#print(len(state_names))

# step = num days
def df_step(df, step=10):
    # get earliest date
    new_df = pd.DataFrame(columns=df.columns)

    date = (min(df['Date']).to_pydatetime())

    date_increments = [date]
    while date < max(df['Date']).to_pydatetime():
        #print(date)
        new_df = pd.concat([new_df, df.loc[df.Date.eq(date)]])
        date += timedelta(days=step)
        date_increments.append(date)

    return new_df, date_increments

def slider_steps(step, date_increments):
    k = range(0,len(date_increments)*step, step)
    v = [date_increments[i].strftime('%b %d') for i in range(len(date_increments))]

    return dict(zip(k,v)), dict(zip(k,date_increments))

df = JHCovid().get()
df = df[(df['Province/State'].isin(state_names))]

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "data/")


external_stylesheets = ['styles.css']

with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    states = json.load(response)

step = 10
test_df, date_increments = df_step(df, step)
slider_marks, value_marks = slider_steps(step, date_increments)

#print(slider_marks)

jh = JHCovid()
df_month = jh.get()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Slider(
                    id='my-slider',
                    min=min(slider_marks),
                    max=max(slider_marks),
                    step=step,
                    marks=slider_marks,
                    value=min(slider_marks)
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='graph-with-slider'),
                    ],
                    className="two-thirds column"
                ),
                html.Div(
                    [
                        html.H6("New York Times"),
                        html.P("Loading articles...", id="nytimes-content")

                    ],
                    id="nyt-container",
                    className="one-third column container"
                )
            ],
            className="row graph-row"
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='graph2')
                    ],
                    className="one-third column"
                ),
                html.Div(
                    [
                        dcc.Graph(id='graph3')
                    ],
                    className="two-thirds column"
                ),
            ],
            className="row"
        )

    ],
    className=""
)

#MONTHS = ['FEB', 'MAR', 'APR', 'MAY', 'JUN','JUL','AUG','SEP']
#MONTHS_NUM = [2,3,4,5,6,7,8,9]

# DEFAULT_COLORSCALE = [
#     "#f2fffb",
#     "#bbffeb",
#     "#98ffe0",
#     "#79ffd6",
#     "#6df0c8",
#     "#69e7c0",
#     "#59dab2",
#     "#45d0a5",
#     "#31c194",
#     "#2bb489",
#     "#25a27b",
#     "#1e906d",
#     "#188463",
#     "#157658",
#     "#11684d",
#     "#10523e",
# ]

#slider_marks = dict(zip(MONTHS_NUM,MONTHS))

#df_month = pd.read_csv(DATA_DIR+'monthly_covid.csv')


@app.callback(
    [Output('graph-with-slider', 'figure'),
     Output('nytimes-content', 'children'),],
    [Input('my-slider', 'value')])
def update_figure(day_increment):
    # do smallest day, plus day increment to string?
    min_date = (min(test_df['Date']).to_pydatetime())
    goal_date = min_date+timedelta(day_increment)
    filtered_df = test_df[test_df['Date'].map(lambda x: x.to_pydatetime()) == goal_date]

    # filtered_df = df_month[df_month['Date'].map(lambda x: datetime.strptime(x,'%Y-%m-%d').month) == selected_month]
    # filtered_df = df_month[df_month['Date'].map(lambda x: datetime.strptime(x,'%Y-%m-%d').month) == selected_month]

    #print(filtered_df)

    fig = px.choropleth_mapbox(filtered_df, geojson=states, locations='FIPS', color='Confirmed',
                               color_continuous_scale='hot', range_color=(0, 20000),
                               mapbox_style="carto-positron", zoom=2, center={"lat": 37.0902, "lon": -95.7129},
                               hover_name='Confirmed')

    # fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
    #                  size="pop", color="continent", hover_name="country",
    #                  log_x=True, size_max=55)

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, transition_duration=500)

    month_articles = articles[articles['date'].map(lambda x: x.month) == goal_date.month]
    article_html = html.Div([html.A(html.P(c['headline']), href=c['url'], target='_blank') for c in month_articles.iloc])

    return (fig, article_html)


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
