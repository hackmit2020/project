""" Federal Reserve economic data

https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data
"""
import quandl
import us  # https://github.com/unitedstates/python-us
import pandas as pd

from typing import List

from ..data import Data, DataFrame

try:
    from credentials.config import QuandlConfig
    quandl.ApiConfig.api_key = QuandlConfig.api_key
except ModuleNotFoundError:
    import os
    quandl.ApiConfig.api_key = os.environ.get("quandl_api_key")


STATES = us.states.mapping('fips', 'abbr', us.STATES)


class Fred(Data):
    NAME = "fred"

    SPECIAL_DATA_SETS = {
        'US': 'FRED/UNRATE',
    }

    def __load_df(self, region):
        if region in self.SPECIAL_DATA_SETS:
            set_name = self.SPECIAL_DATA_SETS[region]
        else:
            set_name = 'FRED/{}UR'.format(region)

        df = quandl.get(set_name, column_index='1')
        #df.rename(columns={'Value': region}, inplace=True)
        df.rename(columns={'Value': 'Rate'}, inplace=True)
        return df

    def _remote_load(self) -> DataFrame:
        print("Remote loading FRED data...")

        data_sets: List[DataFrame] = []

        for fips, region in STATES.items():  # + ['US']
            print(region)
            df = self.__load_df(region)
            df['Region'] = region
            df['fips'] = fips

            data_sets.append(df)


        data = pd.concat(data_sets)
        data.rename_axis("Date", inplace=True)
        data.reset_index(inplace=True)
        return data
