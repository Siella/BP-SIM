from typing import List, Sequence

import numpy as np

from scripts.bp_simulator import Measurement
from scripts.rules import Rule, arv_rule, base_rule, sd_rule


class Filter:
    """
    Performs information filtering
    via different rules.
    """
    def __init__(self, rules: List[Rule]):
        self.rules = rules  # not initialized generators

    def fit(self, data: Sequence[Measurement]):
        for rule in self.rules:
            rule.fit(data)

    def apply(self, data: Sequence[Measurement]) -> np.array:
        try:
            return np.array([
                list(rule.apply(data)) for rule in self.rules
            ])
        except ValueError:
            print('Fit a filter first!')


if __name__ == '__main__':
    data = [
        Measurement(120, 60),
        Measurement(110, 80),
        Measurement(70, 40)
    ]
    f = Filter([
                base_rule,
                sd_rule,
                arv_rule,
               ])
    f.fit(data)
    print(f.apply(data))
