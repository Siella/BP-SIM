import math
from typing import Callable, Generator, List, Sequence

import numpy as np

from scripts.bp_simulator import Measurement
from scripts.parameters import CriticalValues


def arv_generator(data: Sequence[Measurement],
                  period: int = 1) -> Generator:
    """
    Arterial real variability (ARV) index for SBP.
    """
    data_zip = list(zip(data[1:], data[:-1]))
    for _ in range(len(data) - 1):
        for i in range(period):
            arv = 0
            for meas_next, meas_prev in data_zip[i: i + period]:
                arv += abs(meas_next.sbp - meas_prev.sbp)
            arv /= period
        yield arv


def arv_rule_generator(data: Sequence[Measurement],
                       period: int = 1) -> Generator:
    """
    Rule generator based on ARV index for SBP.
    """
    arv_values = list(arv_generator(data, period))
    yield lambda x: True  # first blank comparison
    for k, arv in enumerate(arv_values, 1):
        yield lambda x: abs(x.sbp - data[k-1].sbp) <= arv + 3 * math.sqrt(
            sum([(arv_k - np.mean(arv_values)) ** 2 / k
                 for arv_k in arv_values[:k]])
        )


def sd_rule_generator(data: Sequence[Measurement]) -> Generator:
    """
    Rule generator based on standard deviation for SBP.
    """
    sbp_data = [meas.sbp for meas in data]
    for i, _ in enumerate(data):
        yield lambda x: abs(x.sbp - np.mean(sbp_data)) <= \
                        2 * math.sqrt(np.var(sbp_data))


def basic_rule_generator(data: Sequence[Measurement]) -> Generator:
    """
    Marginal rule generator.
    """
    crit = CriticalValues()
    for i, _ in enumerate(data):
        yield lambda x: all([crit.min_sbp <= x.sbp < crit.max_sbp,
                             crit.min_dbp <= x.dbp < crit.max_dbp])


class Filter:
    """
    Performs information filtering
    via different rules.
    """
    def __init__(self, data: Sequence[Measurement], functions: List[Callable]):
        self.data = data
        self.functions = functions  # not initialized generators

    def apply(self) -> np.array:
        return np.array([
            [f(item) for f, item in zip(f_gen(self.data), self.data)]
            for f_gen in self.functions
        ])


if __name__ == '__main__':
    data = [
        Measurement(120, 60),
        Measurement(110, 80),
        Measurement(70, 40)
    ]
    rules = Filter(data,
                   [
                       basic_rule_generator,
                       sd_rule_generator,
                       arv_rule_generator
                   ])
    print(rules.apply())
