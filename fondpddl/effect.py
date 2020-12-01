from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from abc import ABC, abstractmethod, abstractstaticmethod
from fondpddl import Predicate, TypedObject, Argument, ConstType
from fondpddl.utils import Index, get_combinations, AtomSet
from fondpddl.utils.tokens import PddlIter, PddlTree
from typing import List
import fondpddl.condition


class Effect(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_effects(self, state: State, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def get_predicates(self):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractstaticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
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
            eff_type = effects.get(eff, fondpddl.condition.Variable)
        assert issubclass(eff_type, Effect)
        return eff_type.parse(pddl_tree, objects, predicates, types)

    @staticmethod
    def parse_effect(pddl_iter: PddlIter, objects, predicates, types):
        pddl_iter.assert_token(':effect')
        return Effect.parse(pddl_iter.get_group(), objects, predicates, types)


class Init:
    def __init__(self):
        pass

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types, toplevel=False):
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
            eff_type = effects.get(eff, fondpddl.condition.Variable)
        assert issubclass(eff_type, Effect)
        return eff_type.parse(pddl_tree, objects, predicates, types)


class EmptyEffect(Effect):
    def __init__(self):
        pass
    def __str__(self):
        return '()'
    def get_effects(self, state: State, problem: Problem):
        yield AtomSet()

    def get_predicates(self):
        return set(), set()

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_tree.iter_elements().assert_end()
        return EmptyEffect()


class AndEffect(Effect):
    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def get_effects(self, state: State, problem: Problem):
        effects = [list(effect.get_effects(state, problem)) for effect in self.effects]
        for det_effects in get_combinations(effects, AtomSet(), lambda s1,s2: s1.join(s2)):
            yield det_effects

    def get_predicates(self):
        pos = set()
        neg = set()
        for eff in self.effects:
            p1, p2 = eff.get_predicates()
            pos.update(p1)
            neg.update(p2)
        return pos, neg

    def __str__(self):
        return '(AND ' + ' '.join(map(str, self.effects)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('and')
        effects = []
        while pddl_iter.has_next():
            effect = Effect.parse(pddl_iter.get_group(), objects, predicates, types)
            effects.append(effect)
        return AndEffect(effects)

    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('and')
        effects = []
        while pddl_iter.has_next():
            effect = Init.parse(pddl_iter.get_group(), objects, predicates, types)
            effects.append(effect)
        return AndEffect(effects)


class NotEffect(Effect):
    def __init__(self, effect: fondpddl.condition.Variable):
        self.neg_effect = effect

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(negative=[problem.get_variable_index(self.neg_effect)])

    def get_predicates(self):
        neg, pos = self.neg_effect.get_predicates()
        return pos, neg

    def __str__(self):
        return f'(NOT {str(self.neg_effect)})'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('not')
        condition = Effect.parse(pddl_iter.get_group(), objects, predicates, types)
        pddl_iter.assert_end()
        return NotEffect(condition)

    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('not')
        condition = Init.parse(pddl_iter.get_group(), objects, predicates, types)
        pddl_iter.assert_end()
        return NotEffect(condition)


class OneOf(Effect):
    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def get_effects(self, state: State, problem: Problem):
        for effect in self.effects:
            for det_effect in effect.get_effects(state, problem):
                yield det_effect

    def get_predicates(self):
        pos = set()
        neg = set()
        for eff in self.effects:
            p1, p2 = eff.get_predicates()
            pos.update(p1)
            neg.update(p2)
        return pos, neg

    def __str__(self):
        return '(ONEOF ' + ' '.join(map(str, self.effects)) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('oneof')
        effects = []
        while pddl_iter.has_next():
            effect = Effect.parse(pddl_iter.get_group(), objects, predicates, types)
            effects.append(effect)
        return OneOf(effects)

    @staticmethod
    def parse_init(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('oneof')
        effects = []
        while pddl_iter.has_next():
            effect = Init.parse(pddl_iter.get_group(), objects, predicates, types)
            effects.append(effect)
        return OneOf(effects)

class WhenEffect(Effect):
    def __init__(self, condition: fondpddl.condition.Precondition, effect: Effect):
        self.condition = condition
        self.effect = effect

    def get_effects(self, state: State, problem: Problem):
        if self.condition.evaluate(state, problem):
            for effect in self.effect.get_effects(state, problem):
                yield effect
        else:
            for effect in EmptyEffect().get_effects(state, problem):
                yield effect

    def get_predicates(self):
        return self.effect.get_predicates()

    def __str__(self):
        return '(WHEN ' + str(self.condition) + ' ' + str(self.effect) + ')'

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('when')
        condition = fondpddl.condition.Precondition.parse(
                        pddl_iter.get_group(), objects, predicates, types)
        effect = Effect.parse(pddl_iter.get_group(), objects, predicates, types)
        pddl_iter.assert_end()
        return WhenEffect(condition, effect)


