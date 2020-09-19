from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    counties = json.load(response)

import pandas as pd
from data.fred.fred import Fred

f = Fred()
df = f.get()

# TODO: Need to select date

import plotly.express as px

fig = px.choropleth_mapbox(df, geojson=counties, locations='fips', color='Rate',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'unemp':'unemployment rate'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
