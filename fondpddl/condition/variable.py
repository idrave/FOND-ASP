from fondpddl import Predicate, Constant, State, Problem
from fondpddl.condition import Precondition
from typing import List

class Variable(Precondition):
    def __init__(self, predicate: Predicate, constants: List[Constant]):
        self.predicate = predicate
        self.constants = constants
        #TODO: should check arity and type here?
    
    def evaluate(self, state: State, problem: Problem):
        return state.get_value(self, problem)