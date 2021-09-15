from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from abc import ABC, abstractmethod, abstractstaticmethod
from fondpddl import Predicate, TypedObject, Argument, ConstType, Constant
from fondpddl.utils import Index, get_combinations, AtomSet
from fondpddl.utils.atomdict import AtomDict
from fondpddl.utils.tokens import PddlIter, PddlTree
from fondpddl.constant import parse_const_list
from fondpddl.utils.condition_solve import Conjunction, Disjunction, Negation, VariableSet, AlwaysFalse, AlwaysTrue, EqualitySet
from typing import List
import fondpddl.effect

class Precondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def get_condition(self, state: State, action, problem: Problem, static=None):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractstaticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types): #TODO bug: called in subclasses without parse method
        prec = {
            'and' : And,
            'not' : Not,
            'or': Or, #TODO add disjunctive precondition requirement
            'forall': ForAll, #TODO add universal precondition requirement
            '=': Equality
        }
        cond = pddl_tree.iter_elements().get_next()
        if cond == None:
            cond_type = EmptyCondition()
        else: 
            cond_type = prec.get(cond, Variable)
        assert issubclass(cond_type, Precondition)
        precondition = cond_type.parse(pddl_tree, objects, predicates, types)
        return precondition

    @staticmethod
    def parse_precondition(pddl_iter: PddlIter, objects, predicates, types):
        pddl_iter.assert_token(':precondition')
        return Precondition.parse(pddl_iter.get_group(), objects, predicates, types)


class EmptyCondition(Precondition):
    def __init__(self):
        pass

    def __str__(self):
        return '()'

    def get_condition(self, state: State, problem: Problem, static=None):
        return Conjunction([])

    def evaluate(self, state: State, problem: Problem):
        return True

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_tree.iter_elements().assert_end()
        return EmptyCondition()


class And(Precondition):
    def __init__(self, conditions: List[Precondition]):
        self.conditions = conditions

    def evaluate(self, state: State, problem: problem):
        for condition in self.conditions:
            if not condition.evaluate(state, problem):
                return False
        return True

    def get_condition(self, state: State, action, problem: Problem, static=None):
        return Conjunction([condition.get_condition(state, action, problem, static=static) for condition in self.conditions])

    def __str__(self):
        return '(AND ' + ' '.join(map(str, self.conditions)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('and')
        conditions = []
        while pddl_iter.has_next():
            condition = Precondition.parse(pddl_iter.get_group(), objects, predicates, types)
            conditions.append(condition)
        return And(conditions)


class Not(Precondition):
    def __init__(self, condition: Precondition):
        self.condition = condition

    def evaluate(self, state: State, problem: Problem):
        return not self.condition.evaluate(state, problem)

    def get_condition(self, state: State, action, problem: Problem, static=None):
        return Negation(self.condition.get_condition(state, action, problem, static=static), action, problem)

    def __str__(self):
        return f'(NOT {str(self.condition)})'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('not')
        condition = Precondition.parse(pddl_iter.get_group(), objects, predicates, types)
        pddl_iter.assert_end()
        return Not(condition)


class Or(Precondition):
    def __init__(self, conditions: List[Precondition]):
        self.conditions = conditions

    def evaluate(self, state: State, problem: problem):
        for condition in self.conditions:
            if condition.evaluate(state, problem):
                return True
        return False

    def get_condition(self, state: State, action, problem: Problem, static=None):
        return Disjunction([condition.get_condition(state, action, problem, static=static) for condition in self.conditions])

    def __str__(self):
        return '(OR ' + ' '.join(map(str, self.conditions)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('or')
        conditions = []
        while pddl_iter.has_next():
            condition = Precondition.parse(pddl_iter.get_group(), objects, predicates, types)
            conditions.append(condition)
        return Or(conditions)


class Variable(Precondition, fondpddl.effect.Effect):
    def __init__(self, predicate: Predicate, constants: List[TypedObject]):
        self.predicate = predicate
        self.constants = constants
        if len(constants) > len(predicate.arguments):
            raise ValueError(f'Too many arguments for predicate {predicate.name}')
        if len(constants) < len(predicate.arguments):
            raise ValueError(f'Too little arguments for predicate {predicate.name}')
        for param, const in zip(self.predicate.arguments, constants):
            if param.ctype != None and not const.ctype.is_subtype(param.ctype):
                raise ValueError(f'Wrong argument type {const.ctype} for {predicate.name}')
    
    def __str__(self):
        return self.predicate.name+'('+','.join([const.name for const in self.constants])+')'

    def get_condition(self, state: State, action, problem: Problem, static=None):
        if static != None:
            raise NotImplementedError #TODO
            pos, neg = static
            if self.predicate not in pos and self.predicate not in neg:
                return VariableSet(action, self, state, problem)
            else:
                return Conjunction([])
        if all(c.is_ground() for c in self.constants):
            if self.evaluate(state, problem):
                return AlwaysTrue()
            else:
                return AlwaysFalse()
        return VariableSet(action, self, state, problem)

    def get_predicates(self):
        return {self.predicate}, set()

    def ground(self, problem: Problem):
        g = GroundVar(self)
        g.set_id(problem)
        return g

    def evaluate(self, state: State, problem: Problem):
        return state.get_value(self.ground(problem))

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(positive=[problem.get_variable_index(self)])

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        name = pddl_iter.get_name()
        predicate = predicates.get(name, None)
        if predicate == None:
            raise ValueError(f'Unknown predicate {name}')
        params = parse_const_list(pddl_iter, objects)
        if len(params) > len(predicate.arguments):
            raise ValueError(f'Too many arguments for predicate {name}')
        return Variable(predicate, params)
    
    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates, types):
        return Variable.parse(pddl_tree, objects, predicates, types)


class GroundVar(fondpddl.effect.EffectGround):
    def __init__(self, variable: Variable):
        self.predicate = variable.predicate
        self.constants = []
        self.__const_ids = []
        for const in variable.constants:
            if not const.is_ground():
                raise ValueError(f'GroundVar: Constant {const.name} is not grounded.')
            c = const.get_constant()
            self.constants.append(c)
            self.__const_ids.append(c.get_id())
        self.__const_ids = tuple(self.__const_ids)
        self.__id = None
    
    def evaluate(self, state: State, problem: Problem):
        if self.__id == None:
            self.set_id(problem)
        return state.get_value(self)

    def get_id(self):
        if self.__id == None:
            raise ValueError('No id set for variable')
        return self.predicate.get_id(), self.__id

    def set_id(self, problem: Problem):
        self.__id = problem.get_variable_index(self)

    def get_const_ids(self):
        return self.__const_ids

    def is_conditional(self):
        return False

    def get_effects(self, problem:Problem, state:State=None):
        if self.__id == None:
            self.set_id(problem)
        yield AtomDict([self]), AtomDict()

    def __str__(self):
        return self.predicate.name+'('+','.join([const.name for const in self.constants])+')'

    def __hash__(self):
        return hash((self.predicate.get_id(),)+self.get_const_ids())

    def __eq__(self, other):
        if not isinstance(other, GroundVar):
            return False
        if self.predicate.get_id() != other.predicate.get_id():
            return False
        if self.get_const_ids() != other.get_const_ids():
            return False
        return True


class ForAll(Precondition):
    def __init__(self, argument: Argument, condition: Precondition):
        self.argument = argument
        self.condition = condition
    
    def evaluate(self, state: State, problem: Problem):
        for constant in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(constant)
            if not self.condition.evaluate(state, problem):
                return False
            self.argument.reset()
        return True

    def get_condition(self, state: State, action, problem: Problem, static=None):
        cond = []
        for constant in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(constant)
            cond.append(self.condition.get_condition(state, action, problem, static=static))
            self.argument.reset()
        return Conjunction(cond)

    def get_ground_act(self, state: State, problem: Problem):
        ground_acts = set()
        for constant in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(constant)
            ground_acts = ground_acts.union(self.condition.get_ground_act(state, problem))
            self.argument.reset()
        return ground_acts

    def __str__(self):
        return '(FORALL (' + self.argument.name + \
                ((' - ' + self.argument.ctype.name) if self.argument.ctype != None else '') + ')' +\
                str(self.condition) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types): # TODO add types
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('forall')
        arg_iter = pddl_iter.get_group().iter_elements()
        cond_pddl = pddl_iter.get_group()
        pddl_iter.assert_end()
        arg_name = arg_iter.get_param()
        if types != None:
            if arg_iter.has_next():
                arg_iter.assert_token('-')
                arg_type = arg_iter.get_name()
                if arg_type not in types:
                    raise ValueError(f'Unknown type {arg_type}')
                type_ = types[arg_type]
            else:
                type_ = types['object']
        else:
            type_ = None
            
        arg = Argument(arg_name, ctype=type_)
        objects[arg.name] = arg
        condition = Precondition.parse(cond_pddl, objects, predicates, types)
        objects.pop(arg.name)
        return ForAll(arg, condition)


class Equality(Precondition):
    def __init__(self, const1: TypedObject, const2: TypedObject):
        self.const1 = const1
        self.const2 = const2

    def evaluate(self, state: State, problem: Problem):
        if not self.const1.is_ground():
            raise ValueError(f'Equality: Constant {self.const1.name} is not grounded.')
        if not self.const2.is_ground():
            raise ValueError(f'Equality: Constant {self.const2.name} is not grounded.')
        return self.const1.get_constant() == self.const2.get_constant()

    def get_condition(self, state: State, action, problem: Problem, static=None):
        return EqualitySet(action, self.const1, self.const2, problem)

    def __str__(self):
        return "(= %s %s)" % (str(self.const1), str(self.const2))

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('=')
        params = []
        for _ in range(2):
            if pddl_iter.is_next_name():
                param_name = pddl_iter.get_name()
            else:
                param_name = pddl_iter.get_param()
            param = objects.get(param_name, None)
            if param == None:
                raise ValueError(f'Unknown constant/argument {param_name}')
            params.append(param)
        pddl_iter.assert_end()
        return Equality(*params)
        