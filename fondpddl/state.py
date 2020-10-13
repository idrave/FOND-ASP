from fondpddl.utils import StaticBitSet
from fondpddl.condition import Variable
from fondpddl import GroundAction, Problem
from typing import List, Tuple, Optional
#TODO add function to add effects, receiving problem (for variable indexes), and variable list (positive and negative effects)
class State:
    def __init__(self, bitset: StaticBitSet, transitions: Optional[List[Tuple[GroundAction,List[State]]]]):
        self.bitset = bitset
        self.transitions = transitions
        self.expanded = True

    @classmethod
    def open_state(cls, bitset: StaticBitSet):
        state = cls(bitset, None)
        state.expanded = False
        return state

    def get_value(self, variable: Variable, problem: Problem):
        return self.bitset[problem.get_variable_index(variable)]

    def __hash__(self):
        return hash(self.bitset)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.bitset == other.bitset
