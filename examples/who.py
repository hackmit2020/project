from gs_quant.session import GsSession, Environment
from gs_quant.data import Dataset
from datetime import date
from credentials.config import GSConfig

GsSession.use(client_id=GSConfig.client_id, client_secret=GSConfig.client_secret, scopes=('read_product_data',)) # authenticate GS Session with credentials

dataset = Dataset('COVID19_COUNTRY_DAILY_WHO')                          # initialize the dataset
frame = dataset.get_data(countryId='US', start = date(2019,1,1))        # pull the US data into a Pandas dataframe

print(frame)
