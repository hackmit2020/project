import quandl
import plotly.express as px

from credentials.config import QuandlConfig

quandl.ApiConfig.api_key = QuandlConfig.api_key


df = quandl.get('FRED/UNRATE', column_index='1')
fig = px.line(df, x=df.index.values, y="Value", title='Whoo')
fig.show()
#More Datasets https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation
print(type(df))
print(df.head())
print(df.columns.values)

