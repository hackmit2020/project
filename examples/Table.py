import dash_table
import plotly.express as px
from dash import dash
from gs_quant.session import GsSession, Environment
from gs_quant.data import Dataset
from datetime import date
from credentials.config import GSConfig

import numpy as np

import pandas as pd

GsSession.use(client_id=GSConfig.client_id, client_secret=GSConfig.client_secret, scopes=('read_product_data',))

dataset = Dataset('COVID19_COUNTRY_DAILY_WHO')
df = dataset.get_data(countryId='US', start=date(2019, 1, 1))

app = dash.Dash(__name__)
app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
 )

if __name__ == '__main__':
    app.run_server(debug=True)

