""" General data structure """
from abc import ABCMeta, abstractmethod
import pandas as pd
from pandas import DataFrame
from typing import Union
import os
from pathlib import Path

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "bin")


class Data(metaclass=ABCMeta):
    PATH = Path(DATA_DIR)
    NAME = None

    def __init__(self):
        self.local_file = self.PATH.joinpath(self.NAME+'.feather')

    @abstractmethod
    def _remote_load(self) -> DataFrame:
        """ Load remote data """
        pass

    def _local_load(self) -> Union[None, DataFrame]:
        if self.local_file.is_file():
            return pd.read_feather(self.local_file)
        return None

    def get(self) -> DataFrame:
        df = self._local_load()
        if df is None:
            df = self._remote_load()

            if df.__class__ != DataFrame:
                raise ValueError("`_remote_load()` did not return DataFrame instance")

            df.to_feather(self.local_file)

        return df


if __name__ == "__main__":
    print("Loading from:", Data.PATH)
