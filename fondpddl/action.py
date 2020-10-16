from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from fondpddl import State, Problem
from fondpddl.condition import Precondition, Effect
from fondpddl import Argument, Constant
from typing import List


class Action:
    def __init__(self, name: str, parameters: List[Argument],
                 precondition: Precondition, effect: Effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

    def ground(self, constants: List[Constant]):
        if len(constants) != len(self.parameters):
            raise ValueError((f'Action {self.name} requires {len(self.parameters)}'
                              f' parameters, received {len(constants)}'))
        for arg, const in zip(self.parameters, constants):
            if arg.ctype != const.ctype:
                return None
        return GroundAction(self, constants)


class GroundAction:
    def __init__(self, action: Action, constants: List[Constant]):
        self.action = action
        self.constants = constants
        #TODO: should check arity and type here?

    def is_valid(self, state: State, problem: Problem):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)
        return self.action.precondition.evaluate(state, problem)

    def get_effects(self, state: State, problem: Problem):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)
        return self.action.effect.get_effects(state, problem)

    def string(self, problem: Problem):
        return self.action.name + '('+','.join([const.name for const in self.constants]) + ')'

    def print(self, problem: Problem):
        print(self.string(problem))

    def __hash__(self):
        return hash(self.action.name) + sum([hash(const) for const in self.constants])

    def __eq__(self, other):
        if not isinstance(other, GroundAction):
            return False
        if self.action.name != other.action.name:
            return False
        if len(self.constants) != len(other.constants):
            return False
        for const1, const2 in zip(self.constants, other.constants):
            if const1 != const2:
                return False
        return True