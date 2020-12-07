from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from fondpddl import State, Problem
from fondpddl.condition import Precondition, EmptyCondition, GroundVar
from fondpddl.effect import Effect, EmptyEffect
from fondpddl.utils.tokens import PddlIter, PddlTree
from fondpddl.utils import Index, get_combinations, find_combination
from fondpddl.argument import parse_parameters
from fondpddl import Argument, Constant, Predicate, ConstType, ActionParam
from typing import List
import clingo


class Action:
    def __init__(self, name: str, parameters: List[Argument],
                 precondition: Precondition, effect: Effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

    def valid_ground_actions(self, atoms, problem: Problem):
        for objects, natoms in self.precondition.possible_grounding(
                                        self.parameters, [None] * len(self.parameters),
                                        atoms, [], problem):
            for i, obj in enumerate(objects):
                if obj == None:
                    objects[i] = problem.get_constants(ctype=self.parameters[i].ctype)
                else:
                    objects[i] = [obj]

            for objs in get_combinations(objects, [], lambda l, x: l + [x]):
                valid = True
                for natom in natoms:
                    for param in natom.constants:
                        if not param.is_ground():
                            param.ground(objs[param.get_pos()]) #TODO check forall
                    if atoms.is_atom(GroundVar(natom)):
                        valid = False
                    for param in natom.constants:
                        if isinstance(param, Argument):
                            param.reset()
                    if not valid:
                        break
                if not valid:
                    continue
                yield GroundAction(self, objs)

    def ground(self, constants: List[Constant]):
        if len(constants) != len(self.parameters):
            raise ValueError((f'Action {self.name} requires {len(self.parameters)}'
                              f' parameters, received {len(constants)}'))
        for arg, const in zip(self.parameters, constants):
            if arg.ctype != None and not const.has_type(arg.ctype):
                return None #TODO might raise some unexpected behavior
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
        params = [ActionParam(arg, i) for i, arg in enumerate(params)]
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
        self.__problem = problem
        #self.__ground = []
        self.__ground = {}
        valid_params = []
        positive, negative = problem.get_pos_neg_preds()
        for param in self.__action.parameters:
            valid_params.append(self.__problem.get_constants(param.ctype))
        self.__valid_params = valid_params
        total = 1
        for p in valid_params:
            total *= len(p)
        '''
        for params in get_combinations(valid_params, [], lambda l,x: l + [x]):
            ground_act = self.__action.ground(params)
            assert isinstance(ground_act, GroundAction)
            for s0 in problem.get_initial_states():
                if ground_act.is_valid_static(s0, problem, positive, negative):
                    self.__ground.append(ground_act)
                    break
        for i, ground_act in enumerate(self.__ground):
            ground_act.add_id_to_condition(i, problem)
        '''
        for i, params in enumerate(get_combinations(valid_params, [], lambda l,x: l + [x])):
            ground_act = self.__action.ground(params)
            assert isinstance(ground_act, GroundAction)
            ground_act.add_id_to_condition(i, problem)

    def get_valid_actions(self, state: State):
        for g_id in self.__action.precondition.get_ground_act(state, self.__problem):
            if g_id not in self.__ground:
                constants = find_combination(self.__valid_params, g_id)
                self.__ground[g_id] = self.__action.ground(constants)
            yield self.__ground[g_id]


class GroundAction:
    def __init__(self, action: Action, constants: List[Constant]):
        self.action = action
        self.constants = constants
        self.__effect = None
        #TODO: should check arity and type here?

    def add_id_to_condition(self, id, problem):
        self.ground()
        self.action.precondition.add_ground_act(id, problem)
        self.reset()

    def ground(self):
        for param, const in zip(self.action.parameters, self.constants):
            param.ground(const)

    def reset(self):
        for param in self.action.parameters:
            param.reset()

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
        if self.__effect == None:
            self.__effect = self.action.effect.ground(problem)
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