from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from fondpddl import State, Problem
from fondpddl.condition import Precondition, Effect, EmptyCondition, EmptyEffect
from fondpddl.utils.tokens import PddlIter, PddlTree
from fondpddl.utils import Index
from fondpddl.argument import parse_parameters
from fondpddl import Argument, Constant, Predicate, ConstType
from typing import List
import clingo


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
            if arg.ctype != None and not const.has_type(arg.ctype):
                return None
        return GroundAction(self, constants)

    def __str__(self):
        return '(ACTION ' + self.name +'\n\tPARAMETERS (' + ' '.join(map(str, self.parameters)) + ')\n' + \
                (('\tPRECONDITION ' + str(self.precondition) + '\n') if self.precondition != None else '') + \
                (('\tEFFECT ' + str(self.effect) + '\n') if self.effect != None else '') + ')'

    @staticmethod
    def parse_action(pddl_tree: PddlTree, predicates: List[Predicate],
                     constants: List[Constant], types: List[ConstType]):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':action')
        action_name = pddl_iter.get_name()
        pddl_iter.assert_token(':parameters')
        param_tokens = pddl_iter.get_group()
        params = parse_parameters(param_tokens.iter_elements(), types=types)
        preconditions = None
        effects = None
        objects = {obj.name : obj for obj in constants + params}
        preds = {pred.name: pred for pred in predicates}
        while pddl_iter.has_next():
            if pddl_iter.is_next(':precondition'):
                if preconditions != None:
                    raise ValueError('Redefinition of preconditions')
                preconditions = Precondition.parse_precondition(pddl_iter, objects, preds)
            elif pddl_iter.is_next(':effect'):
                if effects != None:
                    raise ValueError('Redefinition of effects')
                effects = Effect.parse_effect(pddl_iter, objects, preds)
            else:
                raise ValueError(f'Unexpected {pddl_iter.get_next()} in action definition')
        preconditions = preconditions if preconditions != None else EmptyCondition()
        effects = effects if effects != None else EmptyEffect()
        return Action(action_name, params, preconditions, effects)

class GroundAction:
    def __init__(self, action: Action, constants: List[Constant]):
        self.action = action
        self.constants = constants
        #TODO: should check arity and type here?

    def is_valid(self, state: State, problem: Problem):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)
        value = self.action.precondition.evaluate(state, problem)
        for param in self.action.parameters:
            param.reset()
        return value

    def is_valid_static(self, state: State, problem: problem, positive, negative):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)
        values = self.action.precondition.evaluate_static(state, problem, positive, negative)
        for param in self.action.parameters:
            param.reset()
        return True in values

    def get_effects(self, state: State, problem: Problem):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)
        for effect in self.action.effect.get_effects(state, problem):
            yield effect
        for param in self.action.parameters:
            param.reset()

    def __str__(self):
        return self.action.name + '('+','.join([const.name for const in self.constants]) + ')'

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

    def encode_clingo(self, problem: Problem, action_index: Index):
        symbols = []
        index = action_index.get_index(self)
        symbols.append(clingo.Function('action', [index]))
        if problem.is_strong_cyclic(self):
            symbols.append(clingo.Function('fair', [index]))
        else:
            const_a, const_b = problem.get_qnp_constraints(self)
            for constraint in const_a:
                symbols.append(clingo.Function('con_A', [index, constraint]))
            for constraint in const_b:
                symbols.append(clingo.Function('con_B', [index, constraint]))
        return symbols

    def id_clingo(self, action_index):
        return clingo.Function('id', [clingo.Function('action',[str(self)]), action_index.get_index(self)])

    @staticmethod
    def parse(pddl_tree: PddlTree, actions: List[Action], objects: List[Constant]):
        pddl_iter = pddl_tree.iter_elements()
        actions = {action.name: action for action in actions}
        objects = {obj.name: obj for obj in objects}
        name = pddl_iter.get_name()
        action = actions.get(name, None)
        if action == None:
            raise ValueError(f'Unknown action {name}')
        args = []
        while pddl_iter.has_next():
            arg_name = pddl_iter.get_name()
            arg = objects.get(arg_name, None)
            if arg == None:
                raise ValueError(f'Unknown constant/argument {arg_name}')
            args.append(arg)
            if len(args) > len(action.parameters):
                raise ValueError(f'Too many arguments for predicate {name}')
        return GroundAction(action, args)