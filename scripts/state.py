"""
Patient state generator.
Now it implements three states:
normal, bad, missing.
"""
from scripts.patient import Patient


class State(Patient):
    def __init__(self):
        self._current_state = None
        super().__init__()

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        self._current_state = state

    def change_state(self):
        pass
