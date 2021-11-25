"""
Simulates patient BP measurements taken.
"""
import random as rd

import numpy as np
import simpy
from scipy.stats import rv_continuous

from scripts.config import config
from scripts.patient import Patient


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

    def __init__(self, patient: Patient):
        env = simpy.Environment()
        self.patient = patient
        self.env = env
        self.take_measure = env.event()
        self.proc_measure = [env.process(self.proc_measure())]
        self.proc_time = env.process(self.proc_time())
        self.measure_done = env.event()
        self.measurements = []

    def proc_time(self):
        while True:
            self.take_measure.succeed()
            self.take_measure = self.env.event()
            yield self.env.timeout(24)

    def proc_measure(self):
        meas_time = 11
        sbp_seq = self.patient.get_sbp_sequence()
        dbp_seq = self.patient.get_dbp_sequence()
        sbp_dist = rvData(sbp_seq)
        diff_dist = rvData(sbp_seq - dbp_seq)
        while True:
            yield self.take_measure
            yield self.env.timeout(meas_time)
            self.patient.change_state()

            if self.patient.current_state == 'normal':
                sbp_val = sbp_dist.rvs()
                dbp_val = sbp_val - diff_dist.rvs()
            if self.patient.current_state == 'bad':
                sigma = rd.randint(1, 3)
                sign = -1 if rd.uniform(0, 1) < 0.5 else 1
                sbp_val = sbp_dist.rvs() + sign * sigma * np.std(sbp_seq)
                diff = diff_dist.rvs()
                diff = diff if sign > 1 else diff / 2  # for some safe
                dbp_val = sbp_val - diff
            if self.patient.current_state == 'missing':
                sbp_val, dbp_val = -1, -1

            self.measurements.append((int(sbp_val), int(dbp_val)))
            self.measure_done.succeed()
            self.measure_done = self.env.event()

    def run_simulation(self, n_days):
        self.measurements = []
        self.env.run(n_days * 24)


if __name__ == '__main__':
    p = Patient(config['Data']['path_to_file'])
    p.state_prob.normal = 0.45
    p.state_prob.bad = 0.35
    p.state_prob.missing = 0.2
    sim = Simulator(p)
    sim.run_simulation(100)
    for meas in sim.measurements:
        print(meas)
