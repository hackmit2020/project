""" Historical Johns Hopkins data loading

Reference: https://towardsdatascience.com/covid-19-data-processing-58aaa3663f6
- Changed URLS to use files labeled as 'archived'
"""

import pandas as pd
import requests
import io
import tempfile

from ..data import Data, DataFrame


class JHCovid(Data):
    NAME = "jhcovid"
    '''
    URLS = {
        'Confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        'Deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
        'Recovered': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
    }
    '''
    URLS = {
        'Confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Confirmed_archived_0325.csv',
        'Deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Deaths_archived_0325.csv',
        'Recovered': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Recovered_archived_0325.csv'
    }

    def _remote_load(self) -> DataFrame:
        data_set = None
        for data_type, source in self.URLS.items():
            r = requests.get(source)
            data = pd.read_csv(io.BytesIO(r.content))

            dates = data.columns[4:]  # Select all dates with data values

            # Unpivot DataFrames into a long format: create values from the wide date columns
            data = data.melt(
                id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
                value_vars=dates,
                var_name='Date',
                value_name=data_type
            )

            # Select only US data
            data = data[data['Country/Region'] == 'US']

            # Start or merge into final data set
            if data_set is None:
                data_set = data
            else:
                data_set = data_set.merge(
                    right=data, how='left', on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long'])

        return data_set
