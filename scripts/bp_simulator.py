"""
Simulates patient BP measurements taken.
"""
import numpy as np
from scipy.stats import rv_continuous

from scripts.patient import Patient
from scripts.state import State


class rvData(rv_continuous):
    data = np.sort(np.random.rand(100))

    def __init__(self, init_data, *args):
        self.data = np.sort(init_data)
        super().__init__(args)

    def _cdf(self, x, *args) -> float:
        idx = int((self.data < x).sum())
        if idx == 0:
            return 0.0
        if idx >= len(self.data):
            return 1.0
        return (idx - 1.0 + (x - self.data[idx - 1]) /
                (self.data[idx] - self.data[idx - 1])) / len(self.data)


class Simulator:
    def __init__(self,
                 patient: Patient,
                 state: State):
        self.patient = Patient()
        self.state = State()
