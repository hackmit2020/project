""" BROKEN """
import datetime
from credentials.config import GSConfig

from gs_quant.data import Dataset
from gs_quant.session import GsSession, Environment

GsSession.use(Environment.PROD, GSConfig.client_id, GSConfig.client_secret, ('read_product_data',))

ds = Dataset('COVID19_COUNTRY_DAILY_CDC')
data = ds.get_data(start=datetime.date(2020, 1, 21), countryId="US")
print(data.head())  # peek at first few rows of data
