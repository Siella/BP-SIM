"""
Class which creates a virtual patient.
"""
import random as rd
from functools import lru_cache

import numpy as np
import pandas as pd

from scripts.config import config
from scripts.parameters import Parameters


class Patient(Parameters):

    def __init__(self, path_to_file: str):
        self.path_to_file = path_to_file
        self.current_state = self.initial_state
        super().__init__(path_to_file)

    @property
    def initial_state(self) -> str:
        return self._initial_state(self.path_to_file)

    @lru_cache
    def _initial_state(self, path_to_file: str) -> str:
        state_dict = vars(self.state_prob)
        return max(state_dict, key=state_dict.get)

    def get_sbp_sequence(self) -> pd.Series:
        return self.read_file(['sbp_col']).dropna()

    def get_dbp_sequence(self) -> pd.Series:
        return self.read_file(['dbp_col']).dropna()

    def change_state(self):
        x = np.random.randint(0, 2)
        toss = rd.uniform(.0, .5) if x == 0 else rd.uniform(.5, 1.0)
        state_dict = vars(self.state_prob)

        for state in sorted(state_dict, key=state_dict.get):
            if state_dict[state] >= toss:
                self.current_state = state
                break


if __name__ == '__main__':
    p = Patient(config['Data']['path_to_file'])
    print(p.sbp_mean, p.dbp_mean, p.current_state)
    p.state_prob.normal = 0.5
    p.state_prob.bad = 0.4
    for _ in range(100):
        print(p.current_state)
        p.change_state()
