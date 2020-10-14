from __future__ import annotations
from fondpddl.utils import BitSet, StaticBitSet, AtomSet
from typing import List, Tuple, Optional
#TODO add function to add effects, receiving problem (for variable indexes), and variable list (positive and negative effects)
class State:
    def __init__(self, bitset: StaticBitSet,
                 transitions: Optional[List[Tuple['GroundAction',List[State]]]] = None,
                 is_goal: Optional[bool] = None):
        self.bitset = bitset
        self.transitions = transitions
        self.expanded = True
        self.is_goal = is_goal

    @classmethod
    def open_state(cls, bitset: StaticBitSet):
        state = cls(bitset)
        state.expanded = False
        return state

    @classmethod
    def from_atomset(cls, atoms: AtomSet):
        bs = BitSet()
        for pos in atoms.positive:
            bs[pos] = 1
        return State.open_state(StaticBitSet(bs))
        #TODO:should use negative?

    def get_value(self, variable: 'Variable', problem: 'Problem'):
        return self.bitset[problem.get_variable_index(variable)]

    def change_values(self, atoms: AtomSet) -> State:
        bs = BitSet.from_bitmask(self.bitset)
        for atom in atoms.get_positive():
            bs[atom] = 1
        for atom in atoms.get_negative():
            bs[atom] = 0
        return State.open_state(StaticBitSet(bs))

    def __hash__(self):
        return hash(self.bitset)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.bitset == other.bitset
