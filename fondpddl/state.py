from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from fondpddl import Problem
from fondpddl import GroundAction, Predicate
from fondpddl.condition import GroundVar
from fondpddl.utils import BitSet, StaticBitSet, AtomSet
from typing import List, Tuple, Optional
from fondpddl.utils.atomdict import StaticAtomDict, AtomDict
import clingo

#TODO: handle expanded better
class State:
    def __init__(self, atoms: StaticAtomDict,
                 transitions: Optional[List[Tuple[GroundAction,List[State]]]] = None,
                 is_init: Optional[bool] = None,
                 is_goal: Optional[bool] = None):
        self.atoms = atoms
        self.transitions = transitions
        self.expanded = True
        self.is_goal = is_goal
        self.is_init = is_init

    def get_atoms(self, predicate):
        return self.atoms.get_atoms(predicate)

    @classmethod
    def open_state(cls, atoms: StaticAtomDict):
        state = cls(atoms)
        state.expanded = False
        return state

    def get_value(self, variable: GroundVar):
        return self.atoms.has(variable)

    def change_values(self, atoms: AtomDict, negate: AtomDict) -> State:
        pos = atoms.difference(negate)
        neg = negate.difference(atoms)
        new_atoms = self.atoms.join(pos).difference(neg)
        return State.open_state(StaticAtomDict(new_atoms))

    def __hash__(self):
        return hash(self.atoms)

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.atoms == other.atoms

    def string(self, problem: Problem):
        variables = [problem.get_variable(p_id, v_id) for p_id, v_id in self.atoms.iter_ids()]
        return '<' + ','.join(list(map(str, variables))) + '>'

    def print_state(self, problem: Problem):
        print(self.string(problem))

    def encode_clingo(self, state_names, action_names):
        name = clingo.Number(state_names.get_index(self))

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
                                [name, clingo.Number(action_names.get_index(action)), clingo.Number(state_names.get_index(s))]))
        return symbols

    def id_clingo(self, state_index, problem):
        return clingo.Function('id', [clingo.Function('state', [clingo.String(self.string(problem))]), clingo.Number(state_index.get_index(self))])

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
