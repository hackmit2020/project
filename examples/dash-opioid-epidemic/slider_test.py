# IMPORTS
import dash
import dash_html_components as html
import dash_core_components as dcc
import us
import os
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
from datetime import datetime, timedelta
from urllib.request import urlopen
import json

from data.jhcovid.jh import JHCovid
from data.nytimes import NYTQuery
from data.gmobility.gm import GMData

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"
px.set_mapbox_access_token(mapbox_access_token)

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

PACKAGE_DIR = os.path.dirname(__file__)
state_pop_dir = os.path.join(PACKAGE_DIR, "data/state_populations.csv")
df_pop = pd.read_csv(state_pop_dir)

population_dictionary = {}
for i in range(len(df_pop)):
    population_dictionary[df_pop.iloc[i]['NAME']] = round(df_pop.iloc[i]['POPESTIMATE2019']/(10**5),3)

#MIN_DATE = datetime(2020,3,15)

# step = num days
def df_step(df, step=10):
    # get earliest date
    new_df = pd.DataFrame(columns=df.columns)

    #date = (min(df['Date']).to_pydatetime())
    date = MIN_DATE
    date_increments = []

    while date < max(df['Date']).to_pydatetime():
        date_increments.append(date)
        #print(date)
        new_df = pd.concat([new_df, df.loc[df.Date.eq(date)]])
        date += timedelta(days=step)

    return new_df, date_increments


def slider_steps(step, date_increments):
    k = range(0,len(date_increments)*step, step)
    v = [date_increments[i].strftime('%b %d') for i in range(len(date_increments))]

    return dict(zip(k,v)), dict(zip(k,date_increments))

with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    states = json.load(response)

mb = GMData()
mobility = mb.get()

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "data/")

df = JHCovid().get()
df_all_data = df[(df['Province/State'].isin(state_names))]
MIN_DATE = (min(df_all_data['Date']).to_pydatetime())
external_stylesheets = ['styles.css']

step = 10
step_df, date_increments = df_step(df_all_data, step)
slider_marks, value_marks = slider_steps(step, date_increments)
slider_set = (datetime(2020,5,15) - MIN_DATE).days
slider_set = int(slider_set - (slider_set%step))

population_list = []
normalized_change = []
for i in range(len(step_df)):
    #print(step_df.iloc[i]["Province/State"])
    #print(population_dictionary[step_df.iloc[i]["Province/State"]])
    #print(step_df.iloc[i]["Change"])
    try:
        population = population_dictionary[step_df.iloc[i]["Province/State"]]
        population_list.append(population)

        print('SUCCESS')
        print()
    except:
        print('FAIL')
        print()
        population = 10
        population_list.append(population)
        # normalized_change.append(step_df.iloc[i]["Change"]/0.5)

    try:
         norm_change = step_df.iloc[i]["Change"] / population
         normalized_change.append(round(norm_change,2))

    except:
         normalized_change.append(0)

print(population_list)
step_df['Population'] = population_list
step_df['Cases per 100,000 people'] = normalized_change

#jh = JHCovid()
#df_month = jh.get()

state_select_options = [
    {"label": str(state.name), "value": state.fips}
    for state in us.STATES
]

mobility_select_options = [
    {"label": name.replace("_", " "), "value": name}
    for name in ['retail_and_recreation_percent_change_from_baseline',
                 'grocery_and_pharmacy_percent_change_from_baseline',
                 'parks_percent_change_from_baseline',
                 'transit_stations_percent_change_from_baseline',
                 'workplaces_percent_change_from_baseline',
                 'residential_percent_change_from_baseline']
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("COVis"),
                html.H6("HackMIT 2020")
            ]
        ),
        html.Div(
            [
                dcc.Slider(
                    id='my-slider',
                    min=min(slider_marks),
                    max=max(slider_marks),
                    step=step,
                    marks=slider_marks,
                    value=slider_set
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
                        html.H5("New York Times"),
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
                        html.P("Select state to analyze:",className='panel-text'),
                        dcc.Dropdown(
                            id="state-selection",
                            options=state_select_options,
                            multi=False,
                            value='44',
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="mobility-selection",
                            options=mobility_select_options,
                            multi=False,
                            value='retail_and_recreation_percent_change_from_baseline',
                            className="dcc_control",
                        ),
                        dcc.Checklist(
                            id="county-show",
                            options=[
                                {'label': 'Separate counties', 'value': 'county'},
                            ],
                            value=[],
                            className="dcc_control"
                        )

                    ],
                    className="one-third column panel"
                ),
                html.Div(
                    [
                        dcc.Graph(id='mobility')
                    ],
                    className="two-thirds column"
                ),
            ],
            className="row"
        ),
        html.Div(
            html.P("Hacked by Lucien Gaitskell, Portia Gaitskell '23, & William Kopans", id="footer")
        )

    ],
    className=""
)

#MONTHS = ['FEB', 'MAR', 'APR', 'MAY', 'JUN','JUL','AUG','SEP']
#MONTHS_NUM = [2,3,4,5,6,7,8,9]


#slider_marks = dict(zip(MONTHS_NUM,MONTHS))

#df_month = pd.read_csv(DATA_DIR+'monthly_covid.csv')


@app.callback(
    [Output('graph-with-slider', 'figure'),
     Output('nytimes-content', 'children'),],
    [Input('my-slider', 'value')])
def update_figure(day_increment):
    # do smallest day, plus day increment to string?

    goal_date = MIN_DATE+timedelta(day_increment)
    filtered_df = step_df[step_df['Date'].map(lambda x: x.to_pydatetime()) == goal_date]

    # filtered_df = df_month[df_month['Date'].map(lambda x: datetime.strptime(x,'%Y-%m-%d').month) == selected_month]
    # filtered_df = df_month[df_month['Date'].map(lambda x: datetime.strptime(x,'%Y-%m-%d').month) == selected_month]

    #print(filtered_df)

    fig = px.choropleth_mapbox(filtered_df, geojson=states, locations='FIPS', color='Cases per 100,000 people',
                               color_continuous_scale='viridis_r', range_color=(0, 60),
                               mapbox_style=mapbox_style, zoom=2, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=1,
                               hover_name='Cases per 100,000 people')
    #fig.colorbar.Title('Title')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, transition_duration=500)

    month_articles = articles[articles['date'].map(lambda x: x.month) == goal_date.month]
    article_html = html.Div([html.A(html.P(c['headline']), href=c['url'], target='_blank') for c in month_articles.iloc])

    return (fig, article_html)


@app.callback(
    Output("mobility", "figure"),
    [
        Input("state-selection", "value"),
        Input("mobility-selection", "value"),
        Input("county-show", "value"),
    ],
)
def update_production_text(state, mobility_set, county_show):
    print(state)
    state_mobility = mobility[mobility['sub_region_1'] == us.states.lookup(state).name]
    #print(state_mobility)
    state_mobility.dropna(subset=['sub_region_2'], inplace=True)
    print("SUM", state_mobility.isna().sum())

    kwargs = {}
    if county_show:
        kwargs['color'] = 'sub_region_2'
    else:
        state_mobility = state_mobility.groupby(state_mobility['date']).mean()
        state_mobility.reset_index(inplace=True)
    fig = px.line(state_mobility, x='date', y=mobility_set, **kwargs)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
