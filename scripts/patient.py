"""
Class which creates a virtual patient.
"""
import random as rd
from functools import lru_cache

from scripts.parameters import Parameters, config


class Patient(Parameters):

    def __init__(self, path_to_file: str):
        self.path_to_file = path_to_file
        self.current_state = self.initial_state
        super().__init__(path_to_file)

    @property
    def initial_state(self) -> str:
        return self._initial_state(self.path_to_file)

    @lru_cache
    def _initial_state(self, path_to_file: str):
        state_dict = vars(self.state_prob)
        return max(state_dict, key=state_dict.get)

    def change_state(self):
        toss = rd.uniform(0, 1)
        state_dict = vars(self.state_prob)

        def maintain_state() -> bool:
            return state_dict[self.current_state] >= toss

        if not maintain_state():
            for state in sorted(state_dict, key=state_dict.get)[::-1]:
                if state_dict[state] >= toss:
                    self.current_state = state
                    break


if __name__ == '__main__':
    p = Patient(config['Data']['path_to_file'])
    print(p.sbp_mean, p.dbp_mean, p.current_state)
    p.state_prob.normal = 0.1
    p.state_prob.bad = 0.9
    for _ in range(10):
        print(p.current_state)
        p.change_state()
