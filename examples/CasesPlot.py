import dash_table
import plotly.express as px
from dash import dash
from gs_quant.session import GsSession, Environment
from gs_quant.data import Dataset
from datetime import date
from credentials.config import GSConfig

from gs_quant.timeseries import datetime

import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

GsSession.use(client_id=GSConfig.client_id, client_secret=GSConfig.client_secret, scopes=('read_product_data',))

dataset = Dataset('COVID19_COUNTRY_DAILY_WHO')
# df = dataset.get_data(countryId='US', start=date(2019, 1, 1))

# fig = px.line(df, x=df.index.values, y="totalConfirmed", title='Total Confirmed Over Time')
# fig.show()
#
# fig = px.line(df, x=df.index.values, y="newFatalities", title='Total Confirmed Over Time')
# fig.show()

df = dataset.get_data(start=date(2019, 1, 1), limit=20)
# ds = Dataset('COVID19_COUNTRY_DAILY_CDC')
# data = ds.get_data(datetime.date(2020, 1, 21), countryId=[""], limit=50)
print(df.head())  # peek at first few rows of data

# px.scatter(AllCountries, x=AllCountries.values(np.float64).columns, y='totalConfirmed', trendline='ols',
#           facet_col="variable", facet_col_wrap=3).update_xaxes(matches=None)
