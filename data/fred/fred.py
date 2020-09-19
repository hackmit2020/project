""" Federal Reserve economic data

https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data
"""
import quandl

from credentials.config import QuandlConfig

from ..data import Data, DataFrame

quandl.ApiConfig.api_key = QuandlConfig.api_key


STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

class Fred(Data):
    NAME = "fred"

    SPECIAL_DATA_SETS = {
        'US': 'FRED/UNRATE',
    }

    def _remote_load(self) -> DataFrame:
        print("Remote loading FRED data...")

        data_set: DataFrame = None

        for region in STATES + ['US']:
            if region in self.SPECIAL_DATA_SETS:
                set_name = self.SPECIAL_DATA_SETS[region]
            else:
                set_name = 'FRED/{}UR'.format(region)

            df = quandl.get(set_name, column_index='1')
            df.rename(columns={'Value': region}, inplace=True)

            if data_set is None:
                data_set = df
            else:
                data_set = data_set.merge(right=df, how='left', on=['Date'])
            print(region)

        data_set.reset_index(inplace=True, drop=True)
        return data_set
