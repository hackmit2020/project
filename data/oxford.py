""" Oxford data loading """
import pandas as pd
import requests
import io
import us

from .data import Data, DataFrame


class Oxford(Data):
    NAME = "oxford"

    def _remote_load(self) -> DataFrame:
        r = requests.get("https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv")
        df = pd.read_csv(io.BytesIO(r.content))

        df = df[df['CountryCode'] == "USA"]  # Select US only
        source_map = us.states.mapping('abbr', 'fips')
        final_map = {}

        for name, fip in source_map.items():
            final_map['US_' + name] = fip

        df['FIPS'] = df['RegionCode'].map(final_map)
        df.reset_index(inplace=True, drop=True)
        return df
