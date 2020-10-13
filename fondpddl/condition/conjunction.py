from fondpddl.condition import Precondition, Effect
from fondpddl import State, Problem
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