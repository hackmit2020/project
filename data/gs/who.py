""" WHO Data loading

https://developer.gs.com/docs/covid/data/datasets/who/
"""
from datetime import date

from gs_quant.data import Dataset

from .gs import GSData, DataFrame


class WHOData(GSData):
    NAME = "who"

    def _remote_load(self) -> DataFrame:
        dataset = Dataset('COVID19_COUNTRY_DAILY_WHO')  # initialize the dataset
        frame = dataset.get_data(countryId='US', start=date(2019, 1, 1))  # pull the US data into a Pandas dataframe
        frame.reset_index(inplace=True)
        return frame
