from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from fondpddl import Predicate, Constant, TypedObject
from fondpddl.utils import AtomSet
from fondpddl.condition import Precondition, Effect
from typing import List

class Variable(Precondition, Effect):
    def __init__(self, predicate: Predicate, constants: List[TypedObject]):
        self.predicate = predicate
        self.constants = constants
        #TODO: should check arity and type here?
    
    def __str__(self):
        return self.predicate.name+'('+','.join([const.name for const in self.constants])+')'

    def evaluate(self, state: State, problem: Problem):
        return state.get_value(self, problem)

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(positive=[problem.get_variable_index(self)])