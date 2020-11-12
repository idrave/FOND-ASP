from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from abc import ABC, abstractmethod, abstractstaticmethod
from fondpddl import Predicate, TypedObject
from fondpddl.utils import Index, get_combinations, AtomSet
from fondpddl.utils.tokens import PddlIter, PddlTree
from typing import List


class Effect(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_effects(self, state: State, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractstaticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        effects = {
            'and' : AndEffect,
            'not' : NotEffect,
            'oneof': OneOf,
            'when': WhenEffect #TODO add conditional effect requirement
        }
        eff = pddl_tree.iter_elements().get_next()
        if eff == None:
            eff_type = EmptyEffect()
        else:
            eff_type = effects.get(eff, Variable)
        assert issubclass(eff_type, Effect)
        return eff_type.parse(pddl_tree, objects, predicates)

    @staticmethod
    def parse_effect(pddl_iter: PddlIter, objects, predicates):
        pddl_iter.assert_token(':effect')
        return Effect.parse(pddl_iter.get_group(), objects, predicates)

class Init:
    def __init__(self):
        pass

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, toplevel=False):
        effects = {
            'oneof': OneOf
        }
        if not toplevel:
            effects['and'] = AndEffect
            effects['not'] = NotEffect
        eff = pddl_tree.iter_elements().get_next()
        if eff == None:
            eff_type = EmptyEffect()
        else:
            eff_type = effects.get(eff, Variable)
        assert issubclass(eff_type, Effect)
        return eff_type.parse(pddl_tree, objects, predicates)

class EmptyEffect(Effect):
    def __init__(self):
        pass
    def __str__(self):
        return '()'
    def get_effects(self, state: State, problem: Problem):
        yield AtomSet()
    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_tree.iter_elements().assert_end()
        return EmptyEffect()


class Precondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractstaticmethod
    def parse(pddl_tree: PddlTree, objects, predicates): #TODO bug: called in subclasses without parse method
        prec = {
            'and' : And,
            'not' : Not,
            'or': Or #TODO add disjunctive precondition requirement
        }
        cond = pddl_tree.iter_elements().get_next()
        if cond == None:
            cond_type = EmptyCondition()
        else: 
            cond_type = prec.get(cond, Variable)
        assert issubclass(cond_type, Precondition)
        precondition = cond_type.parse(pddl_tree, objects, predicates)
        return precondition

    @staticmethod
    def parse_precondition(pddl_iter: PddlIter, objects, predicates):
        pddl_iter.assert_token(':precondition')
        return Precondition.parse(pddl_iter.get_group(), objects, predicates)


class EmptyCondition(Precondition):
    def __init__(self):
        pass
    def __str__(self):
        return '()'
    def evaluate(self, state: State, problem: Problem):
        return True
    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_tree.iter_elements().assert_end()
        return EmptyEffect()


class And(Precondition):
    def __init__(self, conditions: List[Precondition]):
        self.conditions = conditions

    def evaluate(self, state: State, problem: problem):
        for condition in self.conditions:
            if not condition.evaluate(state, problem):
                return False
        return True

    def __str__(self):
        return '(AND ' + ' '.join(map(str, self.conditions)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('and')
        conditions = []
        while pddl_iter.has_next():
            condition = Precondition.parse(pddl_iter.get_group(), objects, predicates)
            conditions.append(condition)
        return And(conditions)


class AndEffect(Effect):
    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def get_effects(self, state: State, problem: Problem):
        effects = [list(effect.get_effects(state, problem)) for effect in self.effects]
        for det_effects in get_combinations(effects, AtomSet(), lambda s1,s2: s1.join(s2)):
            yield det_effects

    def __str__(self):
        return '(AND ' + ' '.join(map(str, self.effects)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('and')
        effects = []
        while pddl_iter.has_next():
            effect = Effect.parse(pddl_iter.get_group(), objects, predicates)
            effects.append(effect)
        return AndEffect(effects)

    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('and')
        effects = []
        while pddl_iter.has_next():
            effect = Init.parse(pddl_iter.get_group(), objects, predicates)
            effects.append(effect)
        return AndEffect(effects)


class Not(Precondition):
    def __init__(self, condition: Precondition):
        self.condition = condition

    def evaluate(self, state: State, problem: Problem):
        return not self.condition.evaluate(state, problem)

    def __str__(self):
        return f'(NOT {str(self.condition)})'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('not')
        condition = Precondition.parse(pddl_iter.get_group(), objects, predicates)
        pddl_iter.assert_end()
        return Not(condition)

class NotEffect(Effect):
    def __init__(self, effect: Variable):
        self.neg_effect = effect

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(negative=[problem.get_variable_index(self.neg_effect)])

    def __str__(self):
        return f'(NOT {str(self.neg_effect)})'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('not')
        condition = Effect.parse(pddl_iter.get_group(), objects, predicates)
        pddl_iter.assert_end()
        return NotEffect(condition)

    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('not')
        condition = Init.parse(pddl_iter.get_group(), objects, predicates)
        pddl_iter.assert_end()
        return NotEffect(condition)

class Or(Precondition):
    def __init__(self, conditions: List[Precondition]):
        self.conditions = conditions

    def evaluate(self, state: State, problem: problem):
        for condition in self.conditions:
            if condition.evaluate(state, problem):
                return True
        return False

    def __str__(self):
        return '(OR ' + ' '.join(map(str, self.conditions)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('or')
        conditions = []
        while pddl_iter.has_next():
            condition = Precondition.parse(pddl_iter.get_group(), objects, predicates)
            conditions.append(condition)
        return Or(conditions)

class OneOf(Effect):
    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def get_effects(self, state: State, problem: Problem):
        for effect in self.effects:
            for det_effect in effect.get_effects(state, problem):
                yield det_effect

    def __str__(self):
        return '(ONEOF ' + ' '.join(map(str, self.effects)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('oneof')
        effects = []
        while pddl_iter.has_next():
            effect = Effect.parse(pddl_iter.get_group(), objects, predicates)
            effects.append(effect)
        return OneOf(effects)

    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('oneof')
        effects = []
        while pddl_iter.has_next():
            effect = Init.parse(pddl_iter.get_group(), objects, predicates)
            effects.append(effect)
        return OneOf(effects)


class WhenEffect(Effect):
    def __init__(self, condition: Precondition, effect: Effect):
        self.condition = condition
        self.effect = effect

    def get_effects(self, state: State, problem: Problem):
        if self.condition.evaluate(state, problem):
            for effect in self.effect.get_effects(state, problem):
                yield effect
        else:
            for effect in EmptyEffect().get_effects(state, problem):
                yield effect

    def __str__(self):
        return '(WHEN ' + str(self.condition) + ' ' + str(self.effect) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('when')
        condition = Precondition.parse(pddl_iter.get_group(), objects, predicates)
        effect = Effect.parse(pddl_iter.get_group(), objects, predicates)
        pddl_iter.assert_end()
        return WhenEffect(condition, effect)

class Variable(Precondition, Effect):
    def __init__(self, predicate: Predicate, constants: List[TypedObject]):
        self.predicate = predicate
        self.constants = constants
        if len(constants) > len(predicate.arguments):
            raise ValueError(f'Too many arguments for predicate {predicate.name}')
        if len(constants) < len(predicate.arguments):
            raise ValueError(f'Too little arguments for predicate {predicate.name}')
        for param, const in zip(self.predicate.arguments, constants):
            if param.ctype != None and param.ctype != const.ctype:
                raise ValueError(f'Wrong argument type {const.ctype} for {predicate.name}')
    
    def __str__(self):
        return self.predicate.name+'('+','.join([const.name for const in self.constants])+')'

    def evaluate(self, state: State, problem: Problem):
        return state.get_value(self, problem)

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(positive=[problem.get_variable_index(self)])

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates):
        pddl_iter = pddl_tree.iter_elements()
        name = pddl_iter.get_name()
        predicate = predicates.get(name, None)
        if predicate == None:
            raise ValueError(f'Unknown predicate {name}')
        params = []
        while pddl_iter.has_next():
            if pddl_iter.is_next_name():
                param_name = pddl_iter.get_name()
            else:
                param_name = pddl_iter.get_param()
            param = objects.get(param_name, None)
            if param == None:
                raise ValueError(f'Unknown constant/argument {param_name}')
            params.append(param)
            if len(params) > len(predicate.arguments):
                raise ValueError(f'Too many arguments for predicate {name}')
        return Variable(predicate, params)
    
    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates):
        return Variable.parse(pddl_tree, objects, predicates)