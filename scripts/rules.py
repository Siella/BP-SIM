import math
from typing import Callable, Generator, Sequence, Tuple

import numpy as np
from scipy.interpolate import interp1d

from scripts.bp_simulator import Measurement
from scripts.parameters import CriticalValues


def arv_generator(data: Sequence[float]) -> Generator:
    """
    Arterial real variability (ARV) index for SBP / DBP.
    """
    x = np.array(range(len(data)))
    y = np.array(data)
    y = np.where(y == -1, np.nan, y)
    idx_finite = np.isfinite(y)
    if len(idx_finite) < 2:
        raise ValueError('Not enough values to generate!')
    f_interp = interp1d(x[idx_finite], y[idx_finite])
    data_interp = f_interp(x)

    arv = 0
    for i in range(len(data_interp) - 1):
        meas_prev, meas_next = data_interp[i], data_interp[i+1]
        arv += abs(meas_next - meas_prev)
        yield arv / len(data_interp[:i+1])
    yield arv / len(data_interp)


def arv_rule_fit(data: Sequence[Measurement]) -> Tuple:
    sbp_vals = [x.sbp for x in data]
    dbp_vals = [x.dbp for x in data]
    arv_sbp_vals = list(arv_generator(sbp_vals))
    arv_dbp_vals = list(arv_generator(dbp_vals))
    return (np.mean(sbp_vals), np.mean(dbp_vals),
            np.mean(arv_sbp_vals), np.mean(arv_dbp_vals),
            np.var(arv_sbp_vals), np.var(arv_dbp_vals))


def arv_rule_generator(data: Sequence[Measurement],
                       args, sigma: int = 3) -> Generator:
    """
    Rule generator based on ARV index for SBP / DBP.
    """
    def try_except_iteration(values: Sequence[float],
                             except_value: float) -> float:
        try:
            prev = next(x for x in values if x != -1)
        except StopIteration:
            prev = except_value
        return prev
    sbp_mean, dbp_mean = args[:2]
    arv_sbp_mean, arv_dbp_mean, arv_sbp_var, arv_dbp_var = args[2:]
    sbp_vals, dbp_vals = [x.sbp for x in data], [x.dbp for x in data]
    for k in range(len(sbp_vals)):
        x_sbp_prev = try_except_iteration(sbp_vals[:k][::-1], sbp_mean)
        x_dbp_prev = try_except_iteration(dbp_vals[:k][::-1], dbp_mean)
        yield lambda x: all(
            [abs(x.sbp - x_sbp_prev) <= arv_sbp_mean +
             sigma * math.sqrt(arv_sbp_var),
             abs(x.dbp - x_dbp_prev) <= arv_dbp_mean +
             sigma * math.sqrt(arv_dbp_var)]
        )


def sd_rule_fit(data: Sequence[Measurement]) -> Tuple:
    sbp_data = [x.sbp for x in data if x.sbp != -1]
    dbp_data = [x.dbp for x in data if x.dbp != -1]
    return (np.mean(sbp_data), np.mean(dbp_data),
            np.var(sbp_data), np.var(dbp_data))


def sd_rule_generator(data: Sequence[Measurement],
                      args, sigma: int = 2) -> Generator:
    """
    Rule generator based on standard deviation for SBP.
    """
    mean_sbp, mean_dbp, var_sbp, var_dbp = args
    for i, _ in enumerate(data):
        yield lambda x: all(
            (abs(x.sbp - mean_sbp) <= sigma * math.sqrt(var_sbp),
             abs(x.dbp - mean_dbp) <= sigma * math.sqrt(var_dbp))
        )


def basic_rule_fit(data: Sequence[Measurement]) -> None:
    return


def basic_rule_generator(data: Sequence[Measurement], args) -> Generator:
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
        try:
            fit_func = globals()[fit_func_name]
        except KeyError:
            raise KeyError(f'Fit function is not defined for {func_name}!')
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
        Measurement(-1, -1),
        Measurement(70, 40)
    ]
    data_1 = [
        Measurement(60, 40),
        Measurement(190, 30)
    ]
    arv_rule = Rule(arv_rule_generator)
    arv_rule.fit(data)
    print(arv_rule.apply(data_1))
