from scripts.bp_simulator import Measurement
from scripts.filter import Filter
from scripts.rules import arv_rule, base_rule, sd_rule

data = [
    Measurement(120, 60),
    Measurement(110, 80),
    Measurement(70, 40)
]


def test_basic_rule():
    f = Filter([base_rule])
    f.fit(data)
    assert f.apply(data).tolist() == [[False, True, False]]


def test_sd_rule():
    f = Filter([sd_rule])
    f.fit(data)
    assert f.apply(data).tolist() == [[True, True, True]]


def test_arv_rule():
    f = Filter([arv_rule])
    f.fit(data)
    assert f.apply(data).tolist() == [[True, True, False]]
