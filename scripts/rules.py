import math
from typing import Callable, Generator, Sequence, Tuple

import numpy as np

from scripts.bp_simulator import Measurement
from scripts.parameters import CriticalValues


def arv_generator(data: Sequence[Measurement]) -> Generator:
    """
    Arterial real variability (ARV) index for SBP.
    """
    data_zip = list(zip(data[1:], data[:-1]))
    arv = 0
    for i in range(len(data) - 1):
        for meas_next, meas_prev in data_zip:
            if meas_next.sbp * meas_prev.sbp > 1:  # not missing measurements
                arv += abs(meas_next.sbp - meas_prev.sbp)
        yield arv / len(data[:i+1])


def arv_rule_fit(data: Sequence[Measurement]) -> Tuple:
    arv_values = list(arv_generator(data))
    return np.mean(arv_values), np.var(arv_values)


def arv_rule_generator(data: Sequence[Measurement], args) -> Generator:
    """
    Rule generator based on ARV index for SBP.
    """
    mean, var = args
    arv_values = list(arv_generator(data))
    yield lambda x: True  # first blank comparison
    for k, arv in enumerate(arv_values, 1):
        try:
            x_prev = next(x for x in data[k-1::-1] if x.sbp != -1).sbp
        except StopIteration:
            x_prev = mean
        yield lambda x: abs(x.sbp - x_prev) <= arv + 3 * math.sqrt(var)


def sd_rule_fit(data: Sequence[Measurement]) -> Tuple:
    sbp_data = [x.sbp for x in data]
    return np.mean(sbp_data), np.var(sbp_data)


def sd_rule_generator(data: Sequence[Measurement], args) -> Generator:
    """
    Rule generator based on standard deviation for SBP.
    """
    mean, var = args
    for i, _ in enumerate(data):
        yield lambda x: abs(x.sbp - mean) <= 2 * math.sqrt(var)


def basic_rule_fit(data: Sequence[Measurement]) -> None:
    return


def basic_rule_generator(data: Sequence[Measurement], *args) -> Generator:
    """
    Marginal rule generator.
    """
    crit = CriticalValues()
    for i, _ in enumerate(data):
        yield lambda x: all([crit.min_sbp <= x.sbp < crit.max_sbp,
                             crit.min_dbp <= x.dbp < crit.max_dbp])


class Rule:
    def __init__(self, function: Callable):
        self.function = function  # generator which returns callable
        self.args = tuple()

    def fit(self, data: Sequence[Measurement]):
        """
        self.function must have a 'fit alias' with a dunder!
        E.g., rule_name_generator needs rule_name_fit.
        """
        func_name = self.function.__name__
        fit_func_name = '_'.join([func_name[:func_name.rfind('_')], 'fit'])
        fit_func = globals()[fit_func_name]
        self.args = fit_func(data)

    def apply(self, data: Sequence[Measurement]) -> np.array:
        return np.array([
            f(item) for f, item in zip(self.function(data, self.args), data)
        ])


base_rule = Rule(basic_rule_generator)
sd_rule = Rule(sd_rule_generator)
arv_rule = Rule(arv_rule_generator)


if __name__ == '__main__':
    data = [
        Measurement(120, 60),
        Measurement(110, 80),
        Measurement(70, 40)
    ]
    data_1 = [
        Measurement(60, 40)
    ]
    arv_rule = Rule(arv_rule_generator)
    arv_rule.fit(data)
    print(arv_rule.apply(data_1))
