"""
Creates parameters for a patient.
"""
import configparser
from functools import lru_cache
from typing import List

import numpy as np
import pandas as pd

config = configparser.ConfigParser()
config.read("../config.ini")
path_to_file = config['Data']['path_to_file']


class StateProbabilities:
    __slot__ = ('normal', 'bad', 'missing')


class Parameters:

    def __init__(self, path: str):
        self.path_to_file = path

    def read_file(self, keys: List[str]) -> pd.DataFrame:
        cols = [config['Data'][key] for key in keys]
        col = cols[0] if len(cols) == 1 else cols
        return pd.read_csv(self.path_to_file,
                           sep='\t',
                           usecols=cols
                           )[col]

    @property
    def sbp_mean(self) -> float:
        return self._sbp_mean(self.path_to_file)

    @lru_cache
    def _sbp_mean(self, path_to_file) -> float:
        return np.mean(self.read_file(['sbp_col']))

    @property
    def dbp_mean(self) -> float:
        return self._dbp_mean(self.path_to_file)

    @lru_cache
    def _dbp_mean(self, path_to_file) -> float:
        return np.mean(self.read_file(['dbp_col']))

    @property
    def trans_prob(self) -> StateProbabilities:
        probs = StateProbabilities()
        probs.normal, probs.bad, probs.missing = 0, 0, 0
        return probs

    def calculate_probs(self):
        # df = self.read_file(['sbp_col', 'dbp_col', 'dt_col'])
        pass


if __name__ == '__main__':
    p = Parameters(path_to_file)
    print(p.sbp_mean, p.dbp_mean, p.trans_prob.normal)
