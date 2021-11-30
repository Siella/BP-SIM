import os
from unittest.mock import patch

import pytest

from scripts.patient import Patient


def get_test_data_path():
    return os.path.join(
        os.path.dirname(__file__),
        'diary_param_for_test.csv'
    )


def test_not_existing_file():
    with pytest.raises(Exception) as excinfo:
        p = Patient('not-existing-path')
        print(p.sbp_mean)
    assert issubclass(excinfo.type, FileNotFoundError)


def test_patient_instance_creation():
    p = Patient(get_test_data_path())
    prob = p.state_prob

    assert round(p.sbp_mean, 1) == 102.7, 'Wrong mean SBP calculation.'
    assert round(p.dbp_mean, 1) == 65.3, 'Wrong mean DBP calculation.'
    assert (.5, .25, .25) == (prob.normal,
                              prob.missing,
                              prob.bad), 'Wrong probabilities calculation.'

    assert p.initial_state == 'normal', 'Wrong initial state.'
    assert p.current_state == p.initial_state, 'Wrong current state.'


@patch("random.uniform")
def test_patient_state_change(mock_uniform):
    mock_uniform.return_value = .2
    p = Patient(get_test_data_path())
    p.change_state()
    assert p.current_state != p.initial_state, 'State was not changed.'
