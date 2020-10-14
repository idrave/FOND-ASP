from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from fondpddl.condition import Precondition, Effect
from fondpddl.utils import get_combinations, AtomSet
from typing import List

class And(Precondition):
    def __init__(self, conditions: List[Precondition]):
        self.conditions = conditions

    def evaluate(self, state: State, problem: problem):
        for condition in self.conditions:
            if not condition.evaluate(state, problem):
                return False
        return True

class AndEffect(Effect):
    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def get_effects(self, state: State, problem: Problem):
        effects = [list(effect.get_effects(state, problem)) for effect in self.effects]
        for det_effects in get_combinations(effects, AtomSet(), lambda s1,s2: s1.join(s2)):
            yield det_effects
            