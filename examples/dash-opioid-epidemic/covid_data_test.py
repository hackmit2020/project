import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os

from data.jhcovid.jh import JHCovid

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
DATA_DIR = os.path.join(PACKAGE_DIR, "data/state_populations.csv")

df = JHCovid().get()


df_pop = pd.read_csv(DATA_DIR)
population_dictionary = {}
for i in range(len(df_pop)):
    population_dictionary[df_pop.iloc[i]['NAME']] = round(df_pop.iloc[i]['POPESTIMATE2019']/(10**6),3)


population_list = []

df_sub = df[df['Province/State'].isin(state_names)]

#print(df_sub)
print(min(df['Date']), max(df['Date']))

for i in range(len(df_sub)):
    try:
        population_list.append(population_dictionary[df_sub.iloc[i]["Province/State"]])
    except:

        population_list.append(0.5)

df_sub['Population'] = population_list
print(df_sub)
# print(df_sub.columns)
#
# #print(df)
# #print(df.columns)
fig = px.scatter(df_sub, x="Confirmed", y="Deaths", animation_frame="Date", animation_group="Province/State",
           size="Population", color="Province/State", hover_name="Province/State",
            log_x=False, size_max=50, range_x=[min(df_sub['Confirmed']),max(df_sub['Confirmed'])],
                 range_y=[min(df_sub['Deaths']),max(df_sub['Deaths'])])

fig["layout"].pop("updatemenus") # optional, drop animation buttons


# Original code
# df = px.data.gapminder()
# fig = px.scatter(df, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
#            size="pop", color="continent", hover_name="country",
#            log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
#
# fig["layout"].pop("updatemenus") # optional, drop animation buttons
#
app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
 ])

app.run_server(debug=True, use_reloader=False)