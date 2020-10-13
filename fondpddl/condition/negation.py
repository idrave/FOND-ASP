from fondpddl.condition import Precondition, Effect, Variable
from fondpddl import State, Problem

class Not(Precondition):
    def __init__(self, condition: Precondition):
        self.condition = condition

    def evaluate(self, state: State, problem: Problem):
        return not self.condition.evaluate(state, problem)

#TODO: fill this
class NotEffect(Effect):
    def __init__(self, effect: Variable):
        pass