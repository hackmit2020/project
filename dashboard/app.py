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

from data.oxford import Oxford
from data.jhcovid.jh import JHCovid
from data.nytimes import NYTQuery
from data.gmobility.gm import GMData
from data.fred.fred import Fred
from data.gs.who import WHOData

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"
px.set_mapbox_access_token(mapbox_access_token)

GRAPH_MARGIN = 20

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

fred = Fred()
econ_data = fred.get()

ox = Oxford()
policy_data = ox.get()

mb = GMData()
mobility = mb.get()

who = WHOData()
who_data = who.get()

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "../examples/dash-opioid-epidemic/data/")

df = JHCovid().get()
df_all_data = df[(df['Province/State'].isin(state_names))]
MIN_DATE = (min(df_all_data['Date']).to_pydatetime())
external_stylesheets = ['styles.css', 'styles2.css']

step = 10
step_df, date_increments = df_step(df_all_data, step)
slider_marks, value_marks = slider_steps(step, date_increments)
slider_set_date = (datetime(2020,5,15) - MIN_DATE).days
slider_set = int(slider_set_date - (slider_set_date%step))

population_list = []
normalized_change = []
for i in range(len(step_df)):
    #print(step_df.iloc[i]["Province/State"])
    #print(population_dictionary[step_df.iloc[i]["Province/State"]])
    #print(step_df.iloc[i]["Change"])
    try:
        population = population_dictionary[step_df.iloc[i]["Province/State"]]
        population_list.append(population)

        #print('SUCCESS')
        #print()
    except:
        #print('FAIL')
        #print()
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

policy_select_options = [
    {"label": name[3:], "value": name}
    for name in [
        'C1_School closing', 'C2_Workplace closing', 'C3_Cancel public events', 'C4_Restrictions on gatherings',
        'C5_Close public transport', 'C6_Stay at home requirements', 'C7_Restrictions on internal movement',
        'C8_International travel controls'
    ]
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("COVis"),
                html.H6("HackMIT 2020"),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [

                        html.P(
                            id="description",
                            children= "Throughout this global pandemic, there have been thousands of sources tracking the pandemic. "
                                      "It is overwhelming as individuals for us to process these incompatible data points "
                                      "and understand how it captures the current state of the country. COVis seeks to address "
                                      "this asymmetry and integrates data on healthcare, economics, media, and legislation, "
                                      "correlated by date. Move the slider to see the progression."
                        ),
                    ],
                    className="two-thirds column"
                ),
                html.Div(
                    [
                        html.Div(id='day-status'),
                        html.A(html.Div("Source: Marquee WHO Data"),
                               href="https://marquee.gs.com/s/developer/datasets/COVID19_COUNTRY_DAILY_WHO",
                               className="annotation"),
                    ],
                    className="one-third column"
                )
            ],
            className="row"
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
            [ #html.P("Heatmap displaying new Covid cases per 100,000 people", id='heatmap-title'),
            html.Div( id='heatmap-container', children=
                    [
                        html.P("Heatmap displaying new Covid cases per 100,000 people", id='heatmap-title'),
                        dcc.Graph(id='graph-with-slider'),
                    ],
                    className="two-thirds column"
                ),
                html.Div(
                    [ html.Img(id="nyt", src=app.get_asset_url("new-york-times-logo-black-and-white.png")),
                        #html.H5("New York Times"),
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
                                ),
                                html.Hr(),
                                dcc.Dropdown(
                                    id="policy-selection",
                                    options=policy_select_options,
                                    multi=False,
                                    value='C1_School closing',
                                    className="dcc_control",
                                ),

                            ],
                            className="row panel"
                        ),
                        html.Div(
                            [
                                html.A(html.P("Oxford Policy Documentation"),
                                       href="https://github.com/OxCGRT/covid-policy-tracker/blob/master/documentation/codebook.md",
                                       target="_blank"),
                                dcc.Graph(id='policy', className="")
                            ],
                            className="row graph",
                            id="policy-container"
                        )
                    ],
                    className="one-third column"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.A(html.P("Google Mobility data", className="graph-title"), href="https://www.google.com/covid19/mobility/",
                                       target="_blank", className="graph-title"),
                                dcc.Graph(id='mobility', className="graph")
                            ],
                            className="row"
                        ),
                        html.Div(
                            [
                                html.A(html.P("State Unemployment rate", className="graph-title"), href="https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data",
                                       target="_blank"),
                                dcc.Graph(id='econ', className="graph")
                            ],
                            className="row"
                        ),
                        html.Div(
                            [
                                html.P("Hacked by Lucien Gaitskell, Portia Gaitskell '23, & William Kopans", id="nametag")
                            ],
                            className="row"
                        )
                    ],
                    className="two-thirds column"
                ),
            ],
            className="row graph-row"
        ),
    ],
    className=""
)

#MONTHS = ['FEB', 'MAR', 'APR', 'MAY', 'JUN','JUL','AUG','SEP']
#MONTHS_NUM = [2,3,4,5,6,7,8,9]


#slider_marks = dict(zip(MONTHS_NUM,MONTHS))

#df_month = pd.read_csv(DATA_DIR+'monthly_covid.csv')


@app.callback(
    [Output('graph-with-slider', 'figure'),
     Output('nytimes-content', 'children'),
     Output('day-status', 'children')
     ],
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
    # fig.update_layout(
    #     font_family="Courier New",
    #     font_color="blue",
    #     title_font_family="Times New Roman",
    #     title_font_color="red",
    #     legend_title_font_color="green"
    # )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, transition_duration=500, title_font_color="white",)

    month_articles = articles[articles['date'].map(lambda x: x.month) == goal_date.month]
    article_html = html.Div([html.A(html.P(c['headline']), href=c['url'], target='_blank') for c in month_articles.iloc])

    if not who_data.empty:
        day_data = who_data.loc[who_data['date'] == goal_date].iloc[0]
        print(day_data)
        status = [
            html.H3("Confirmed: {:}".format(str(int(day_data['totalConfirmed']))), className="status"),
            html.H3("Deaths: {:}".format(str(int(day_data['totalFatalities']))), className="status"),
        ]
    else:
        status = [
        ]

    return (fig, article_html, status)


@app.callback(
    [
        Output("mobility", "figure"),
        Output("policy", "figure"),
        Output("econ", "figure")
    ],
    [
        Input("state-selection", "value"),
        Input("mobility-selection", "value"),
        Input("county-show", "value"),
        Input("policy-selection", "value")
    ],
)
def update_production_text(state, mobility_set, county_show, policy_set):
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
    fig_mobility = px.line(state_mobility, x='date', y=mobility_set, **kwargs)

    state_policy = policy_data[policy_data['RegionCode'] == "US_" + us.states.lookup(state).abbr]
    fig_policy = px.line(state_policy, x='Date', y=policy_set)
    fig_policy.update_layout(margin={"r": GRAPH_MARGIN, "t": GRAPH_MARGIN, "l": GRAPH_MARGIN, "b": GRAPH_MARGIN})

    state_econ = econ_data[econ_data['Region'] == us.states.lookup(state).abbr]
    fig_econ = px.line(state_econ, x='Date', y='Rate')

    return (fig_mobility, fig_policy, fig_econ)


if __name__ == '__main__':
    app.run_server(debug=True)
