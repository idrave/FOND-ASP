from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from fondpddl.condition import Precondition, Effect, Variable
from fondpddl.utils import AtomSet


class Not(Precondition):
    def __init__(self, condition: Precondition):
        self.condition = condition

    def evaluate(self, state: State, problem: Problem):
        return not self.condition.evaluate(state, problem)

class NotEffect(Effect):
    def __init__(self, effect: Variable):
        self.neg_effect = effect

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(negative=[problem.get_variable_index(self.neg_effect)])