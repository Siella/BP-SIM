from scripts.bp_simulator import Measurement
from scripts.filter import (Filter, arv_rule_generator, basic_rule_generator,
                            sd_rule_generator)

data = [
        Measurement(120, 60),
        Measurement(110, 80),
        Measurement(70, 40)
    ]


def test_basic_rules():
    f = Filter(data, [basic_rule_generator])
    assert f.apply().tolist() == [[True, True, False]]


def test_sd_rules():
    f = Filter(data, [sd_rule_generator])
    assert f.apply().tolist() == [[True, True, True]]


def test_arv_rules():
    f = Filter(data, [arv_rule_generator])
    assert f.apply().tolist() == [[True, True, False]]
