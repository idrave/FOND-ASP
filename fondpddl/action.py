from __future__ import annotations

from clingo import symbol
from fondpddl.utils.atomdict import AtomDict
import typing
if typing.TYPE_CHECKING:
    from fondpddl import State, Problem
from fondpddl.condition import Precondition, EmptyCondition, GroundVar
from fondpddl.effect import Effect, EmptyEffect
from fondpddl.utils.tokens import PddlTree
from fondpddl.utils import Index, get_combinations
from fondpddl.argument import parse_parameters, TypedObject
from fondpddl.constant import parse_const_list
from fondpddl import Argument, Constant, Predicate, ConstType, ActionParam
from typing import List, Dict
import clingo


class Action:
    def __init__(self, name: str, parameters: List[Argument],
                 precondition: Precondition, effect: Effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

    def validate_args(self, args: List[TypedObject]):
        if len(args) != len(self.parameters):
            raise ValueError((f'Action {self.name} requires {len(self.parameters)}'
                              f' parameters, received {len(constants)}'))
        for p, arg in zip(self.parameters, args):
            if p.ctype != None and not arg.has_type(p.ctype):
                raise ValueError((f'Action {self.name} parameter {p.name} has type {p.ctype},'
                              f' but received {arg.name} of type {arg.ctype}'))

    def get_applicable(self, state: State, problem: Problem):
        if len(self.parameters) == 0:
            if self.precondition.evaluate(state, problem):
                yield self.ground([])
            return
        cond = self.precondition.get_condition(state, self, problem)

        def recursive(pos, bounds, vals):
            if pos == len(self.parameters):
                yield vals
                return
            consts, b = cond.get(pos, bounds, (vals[-1] if len(vals) else None))
            if not cond.has(pos):
                assert consts == None
                for out in recursive(pos+1, b, vals+[None]):
                    yield out
            else:
                consts = consts if consts is not None else problem.get_constants(self.parameters[pos].ctype)
                for c in consts:
                    for out in recursive(pos+1, b, vals+[c]):
                        yield out
        
        for out in recursive(0, None, []):
            if any(o is None for o in out):
                for i, o in enumerate(out):
                    if o is None:
                        out[i] = problem.get_constants(self.parameters[i].ctype)
                    else:
                        out[i] = [problem.get_constant(o)]
                for comb in get_combinations(out, [], lambda a, b: a+[b]):
                    yield self.ground(comb)
            else:
                constants = list(map(problem.get_constant, out))
                yield self.ground(constants)

    def ground(self, constants: List[Constant]):
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
        if pddl_iter.is_next(':parameters'):
            pddl_iter.assert_token(':parameters')
            param_tokens = pddl_iter.get_group()
            params = parse_parameters(param_tokens.iter_elements(), types=types)
            params = [ActionParam(arg, i) for i, arg in enumerate(params)]
        else:
            params = []
        preconditions = None
        effects = None
        objects = {obj.name : obj for obj in constants + params}
        preds = {pred.name: pred for pred in predicates}
        type_dict = {ty.name: ty for ty in types} if types != None else None
        while pddl_iter.has_next():
            if pddl_iter.is_next(':precondition'):
                if preconditions != None:
                    raise ValueError('Redefinition of preconditions')
                preconditions = Precondition.parse_precondition(pddl_iter, objects, preds, type_dict)
            elif pddl_iter.is_next(':effect'):
                if effects != None:
                    raise ValueError('Redefinition of effects')
                effects = Effect.parse_effect(pddl_iter, objects, preds, type_dict)
            else:
                raise ValueError(f'Unexpected {pddl_iter.get_next()} in action definition')
        preconditions = preconditions if preconditions != None else EmptyCondition()
        effects = effects if effects != None else EmptyEffect()
        return Action(action_name, params, preconditions, effects)

class ProblemAction:
    def __init__(self, action: Action, problem: Problem):
        self.__action = action
        self.__ground = {}

    def get_applicable(self, state: State, problem: Problem):
        for ground_action in self.__action.get_applicable(state, problem):
            g = self.__ground.get(ground_action.get_const_ids(), None)
            if g == None:
                self.__ground[ground_action.get_const_ids()] = ground_action
                g = ground_action
            yield g


class GroundAction:
    def __init__(self, action: Action, constants: List[Constant]):
        action.validate_args(constants)
        self.action = action
        self.constants = constants
        self.__effect = None
        self.__const_ids = (c.id for c in constants)
        self.__atoms = None

    def get_const_ids(self):
        return self.__const_ids

    def ground(self):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)

    def reset(self):
        for param in self.action.parameters:
            param.reset()

    def get_effects(self, state: State, problem: Problem):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)
        if self.__effect == None:
            self.__effect = self.action.effect.ground(problem)
        if problem.store_value_changes() and self.__atoms == None:
            # store the atoms that change
            pos, neg = AtomDict(), AtomDict()
            for effect in self.__effect.get_effects(problem, state):
                pos = pos.join(effect[0].difference(effect[1]))
                neg = neg.join(effect[1].difference(effect[0]))
                yield effect
            self.__atoms = (pos, neg)
        else:
            for effect in self.__effect.get_effects(problem, state):
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

    def encode_clingo(self, problem: Problem, action_index: Index, atoms=False):
        symbols = []
        index = clingo.Number(action_index.get_index(self))
        symbols.append(clingo.Function('action', [index]))
        if atoms and self.__atoms != None:
            pos, neg = self.__atoms
            t = clingo.Number(1)
            f = clingo.Number(0)

            # generate eff/3 facts - eff(K, A, 0/1) : action A makes predicate K false/true
            for p, v in pos.iter_ids():
                p_s, v_s = clingo.Number(p), clingo.Number(v)
                symbols.append(clingo.Function('eff', [clingo.Function('', [p_s, v_s]), index, t]))
            for p, v in neg.iter_ids():
                p_s, v_s = clingo.Number(p), clingo.Number(v)
                symbols.append(clingo.Function('eff', [clingo.Function('', [p_s, v_s]), index, f]))

        const_a, const_b = problem.get_fair_constraints(self)
        for constraint in const_a:
            symbols.append(clingo.Function('con_A', [index, clingo.Number(constraint)]))
        for constraint in const_b:
            symbols.append(clingo.Function('con_B', [index, clingo.Number(constraint)]))
        return symbols

    def id_clingo(self, action_index):
        return clingo.Function('id', [clingo.Function('action',[clingo.String(str(self))]), clingo.Number(action_index.get_index(self))])

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

def parse_action_w_args(pddl_tree: PddlTree, actions: Dict, objects: Dict):
    it = pddl_tree.iter_elements()
    actname = it.get_name()
    action = actions.get(actname, None)
    if action == None: raise ValueError('Unknown action name {actname}')
    args = parse_const_list(it, objects)
    if len(args) != len(action.parameters):
        raise ValueError((f'Action {action.name} requires {len(action.parameters)}'
                            f' parameters, received {len(args)}'))
    return action, args