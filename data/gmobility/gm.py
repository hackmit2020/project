""" Google Mobility Data loading

https://www.google.com/covid19/mobility/
"""
from datetime import date
import tempfile
import requests
import io
import zipfile
import pandas as pd


from ..data import Data, DataFrame


class GMData(Data):
    NAME = "gmobility"
    REGIONAL_URL = "https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip"
    EXTRACT_TARGET = "2020_US_Region_Mobility_Report.csv"

    def _remote_load(self) -> DataFrame:
        r = requests.get(self.REGIONAL_URL)
        tf = tempfile.TemporaryDirectory()

        with zipfile.ZipFile(io.BytesIO(r.content)) as archive:
            if any(f.filename == self.EXTRACT_TARGET for f in archive.infolist()):
                fname = archive.extract(self.EXTRACT_TARGET, tf.name)
                data = pd.read_csv(fname)

                return data

        raise IOError("Could not load Google Mobility data.")
