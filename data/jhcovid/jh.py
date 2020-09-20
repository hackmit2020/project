""" Historical Johns Hopkins data loading

Reference: https://towardsdatascience.com/covid-19-data-processing-58aaa3663f6
- Changed URLS to use files labeled as 'archived'
"""
import zipfile
# import re
import pandas as pd
import requests
import io
import tempfile
import us
from datetime import datetime

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
    ARCHIVE_URLS = {
        'Confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Confirmed_archived_0325.csv',
        'Deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Deaths_archived_0325.csv',
        'Recovered': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Recovered_archived_0325.csv'
    }

    REPO_URL = "https://github.com/CSSEGISandData/COVID-19/archive/master.zip"
    CURRENT_DATA_PREFIX = "COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports_us/"

    def _remote_load_archive(self) -> DataFrame:
        """ Load archived COVID-19 data

        https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data/archived_time_series
        """
        data_set = None
        for data_type, source in self.ARCHIVE_URLS.items():
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

            data['Date'] = pd.to_datetime(data['Date'])

            # Select only US data
            data = data[data['Country/Region'] == 'US']

            # Start or merge into final data set
            if data_set is None:
                data_set = data
            else:
                data_set = data_set.merge(
                    right=data, how='left', on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long'])

        data_set['FIPS'] = data_set['Province/State'].map(us.states.mapping('name', 'fips'))
        # VERY IMPORTANT: must be nullable integer type (Int64)
        data_set['FIPS'] = data_set['FIPS'].astype('Int64', errors='ignore').astype(str)
        return data_set

    def _remote_load_current(self) -> DataFrame:
        """ Load current COVID-19 data

        https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports_us
        """
        r = requests.get(self.REPO_URL)
        td = tempfile.TemporaryDirectory()

        with zipfile.ZipFile(io.BytesIO(r.content)) as archive:
            data_sets = []
            for f in archive.infolist():
                if f.filename.startswith(self.CURRENT_DATA_PREFIX) and f.filename.endswith('.csv'):
                    extract_file = archive.extract(f, td.name)

                    fname = f.filename[len(self.CURRENT_DATA_PREFIX):-len('.csv')]

                    #match = re.search(r'\d{2}-\d{2}-\d{4}.csv', f.filename[len(self.CURRENT_DATA_PREFIX):])
                    date = datetime.strptime(fname, '%m-%d-%Y')

                    data = pd.read_csv(extract_file)

                    data.rename(  # Fix column names for to common values
                        columns={
                            'Country_Region': 'Country/Region',
                            'Province_State': 'Province/State',
                            'Long_': 'Long',
                        },
                        inplace=True)

                    # VERY IMPORTANT: must be nullable integer type (Int64)
                    data['FIPS'] = data['FIPS'].astype('Int64', errors='ignore').astype(str)


                    data['Date'] = date

                    data_sets.append(data)

        return pd.concat(data_sets)

    def _remote_load(self) -> DataFrame:
        archive = self._remote_load_archive()
        current = self._remote_load_current()
        combined_data = pd.concat([archive, current])
        combined_data.reset_index(inplace=True, drop=True)

        return combined_data

