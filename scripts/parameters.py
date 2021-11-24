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
    """
    Now it implements three states:
    normal, bad, missing.
    """
    def __init__(self):
        self.normal = None
        self.bad = None
        self.missing = None


class CriticalValues:
    """
    Critical BP values according medical standards.
    """

    def __init__(self):
        self.max_sbp = 180
        self.min_sbp = 80
        self.max_dbp = 120
        self.min_dbp = 50

    def check_condition(self, sbp: float, dbp: float) -> str:
        if sbp is None or dbp is None:
            return 'missing'
        max_conditions = sbp > self.max_sbp or dbp > self.max_dbp
        min_conditions = sbp < self.min_sbp or dbp < self.min_dbp
        if max_conditions or min_conditions:
            return 'bad'
        return 'normal'


class Parameters:

    def __init__(self, path: str):
        self.path_to_file = path

    def read_file(self, keys: List[str]) -> pd.DataFrame:
        cols = [config['Data'][key] for key in keys]
        col = cols[0] if len(cols) == 1 else cols
        df = pd.read_csv(self.path_to_file,
                         sep='\t',
                         usecols=cols)
        return df[col]

    @property
    def sbp_mean(self) -> float:
        return self._sbp_mean(self.path_to_file)

    @lru_cache
    def _sbp_mean(self, path_to_file) -> float:
        return float(np.mean(self.read_file(['sbp_col'])))

    @property
    def dbp_mean(self) -> float:
        return self._dbp_mean(self.path_to_file)

    @lru_cache
    def _dbp_mean(self, path_to_file) -> float:
        return float(np.mean(self.read_file(['dbp_col'])))

    @property
    def state_prob(self) -> StateProbabilities:
        return self._state_prob(self.path_to_file)

    @lru_cache
    def _state_prob(self, path_to_file) -> StateProbabilities:
        probs = StateProbabilities()
        probs.normal, probs.bad, probs.missing = self.calculate_probs()
        return probs

    def calculate_probs(self):
        crit = CriticalValues()
        state_seq = []
        df = self.read_file(['sbp_col', 'dbp_col', 'dt_col'])
        df = df.set_index(config['Data']['dt_col'])
        df.index = pd.to_datetime(df.index.str[:10])  # without time
        dt_range = pd.date_range(min(df.index), max(df.index))

        def access_df_index(df, index):
            try:
                return df.loc[[index], :]
            except KeyError:
                return pd.DataFrame([[None, None]])

        for dt in dt_range:
            df_accessed = access_df_index(df, dt)
            values = df_accessed.values.tolist()
            for val_pair in values:  # in case of more than one meas. per day
                state_seq.append(crit.check_condition(*val_pair))
        num_of_measurements = len(state_seq)
        return (state_seq.count('normal') / num_of_measurements,
                state_seq.count('bad') / num_of_measurements,
                state_seq.count('missing') / num_of_measurements)


if __name__ == '__main__':
    p = Parameters(path_to_file)
    print(p.sbp_mean, p.dbp_mean, p.state_prob.normal)
    ct = CriticalValues()
    print(ct.check_condition(70, 120))
    p.path_to_file = '{0}/diary_param_one_patient.csv'.format(
        path_to_file[:path_to_file.rfind('/')]
    )
    print(p.sbp_mean, p.dbp_mean, p.state_prob.normal)
