from fondpddl.utils import StaticBitSet
from fondpddl import GroundAction
from typing import List, Tuple, Optional

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

    def __hash__(self):
        return hash(self.bitset)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.bitset == other.bitset
