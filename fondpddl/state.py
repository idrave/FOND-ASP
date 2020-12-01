from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from fondpddl import Problem
from fondpddl import GroundAction, Predicate
from fondpddl.condition import Variable
from fondpddl.utils import BitSet, StaticBitSet, AtomSet
from typing import List, Tuple, Optional
from fondpddl.utils.atomdict import AtomDict
import clingo

#TODO: handle expanded better
class State:
    def __init__(self, bitset: StaticBitSet,
                 transitions: Optional[List[Tuple[GroundAction,List[State]]]] = None,
                 is_init: Optional[bool] = None,
                 is_goal: Optional[bool] = None):
        self.bitset = bitset
        self.atoms = [i for i, b in enumerate(bitset) if b]
        self.transitions = transitions
        self.expanded = True
        self.is_goal = is_goal
        self.is_init = is_init

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

    def true_atoms(self):
        return self.atoms

    def get_atom_dict(self, problem: Problem):
        atoms = AtomDict()
        for i in self.atoms:
            var = problem.get_variable(i)
            atoms.add_atom(var)
        return atoms

    def get_value(self, variable: Variable, problem: Problem):
        return self.bitset[problem.get_variable_index(variable)]

    def change_values(self, atoms: AtomSet) -> State:
        bs = BitSet.from_bitmask(self.bitset)
        for atom in atoms.positive:
            bs[atom] = 1
        for atom in atoms.negative:
            bs[atom] = 0
        return State.open_state(StaticBitSet(bs))

    def __hash__(self):
        return hash(self.bitset)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        if len(self.atoms) != len(other.atoms):
            return False
        for a, b in zip(self.atoms, other.atoms):
            if a != b:
                return False
        return True

    def string(self, problem: Problem):
        variables = [problem.get_variable(i) for i in self.atoms]
        return '<' + ','.join(list(map(str, variables))) + '>'

    def print_state(self, problem: Problem):
        for i, bit in enumerate(self.bitset):
            if bit:
                problem.print_variable(i)

    def encode_clingo(self, state_names, action_names):
        name = state_names.get_index(self)
        symbols = [clingo.Function('state', [name])]
        if self.is_init:
            symbols.append(clingo.Function('initialState', [name]))
        if self.is_goal: 
            symbols.append(clingo.Function('goal', [name]))
        if not self.expanded:
            return symbols
        assert isinstance(self.transitions, list)
        for action, states in self.transitions:
            for s in states:
                symbols.append(clingo.Function('transition',
                                [name, action_names.get_index(action), state_names.get_index(s)]))
        return symbols

    def id_clingo(self, state_index, problem):
        return clingo.Function('id',[clingo.Function('state',[self.string(problem)]), state_index.get_index(self)])

    def set_expanded(self):
        self.expanded = True

    def set_transitions(self, transitions):
        self.transitions = transitions #TODO with nondeterministic effects we might have a repeated (state, action) pair

    def get_transitions(self) -> List[Tuple[GroundAction,List[State]]]:
        if self.transitions == None:
            raise ValueError('State not expanded')
        return self.transitions

    def set_init(self, is_init: bool):
        self.is_init = is_init

    def set_goal(self, is_goal: bool):
        self.is_goal = is_goal

    def get_tuples(self, predicate: Predicate): #TODO What
        pass