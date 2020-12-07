from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from abc import ABC, abstractmethod, abstractstaticmethod
from fondpddl import Predicate, TypedObject, Argument, ConstType
from fondpddl.utils import Index, get_combinations, AtomSet
from fondpddl.utils.atomdict import AtomDict
from fondpddl.utils.tokens import PddlIter, PddlTree
from typing import List, Iterator
import fondpddl.condition


class Effect(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_predicates(self):
        raise NotImplementedError

    @abstractmethod
    def ground(self, problem: Problem):
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

class EffectGround:
    def __init__(self):
        pass

    @abstractmethod
    def get_effects(self, problem: Problem, state: State=None) -> Iterator[AtomDict]:
        raise NotImplementedError

    @abstractmethod
    def is_conditional(self):
        raise NotImplementedError

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


class EmptyEffect(Effect, EffectGround):
    def __init__(self):
        pass

    def __str__(self):
        return '()'

    def get_effects(self, problem: Problem, state: State=None):
        yield AtomDict([]), AtomDict([])

    def get_predicates(self):
        return set(), set()

    def ground(self, problem: Problem):
        return EmptyEffect()

    def is_conditional(self):
        return False

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

    def ground(self, problem: Problem):
        return AndGround([effect.ground(problem) for effect in self.effects], problem)

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

class AndGround(EffectGround):
    def __init__(self, effects: List[EffectGround], problem):
        self.__effects = [(AtomDict(), AtomDict())]
        self.__cond = []
        for effect in effects:
            if effect.is_conditional():
                self.__cond.append(effect)
            else:
                self.__effects = list(get_combinations([self.__effects, list(effect.get_effects(problem))],
                                    (AtomDict([]),AtomDict([])), lambda a, b: (a[0].join(b[0]), a[1].join(b[1]))))
    
    def is_conditional(self):
        return len(self.__cond) > 0

    def get_effects(self, problem: Problem, state: State=None):
        assert not self.is_conditional() or (state != None and problem != None)
        if not self.is_conditional():
            for effect in self.__effects:
                yield effect
            return
        cond_effects = [list(e.get_effects(problem, state)) for e in self.__cond]
        effects = get_combinations([self.__effects]+cond_effects, (AtomDict([]), AtomDict([])),
                                    lambda a, b: (a[0].join(b[0]), a[1].join(b[1])))
        for effect in effects:
            yield effect # tuple with positive and negative atoms


class NotEffect(Effect):
    def __init__(self, effect: fondpddl.condition.Variable):
        self.neg_effect = effect

    def get_predicates(self):
        neg, pos = self.neg_effect.get_predicates()
        return pos, neg

    def ground(self, problem: Problem):
        return NotGround(self.neg_effect.ground(problem), problem)

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


class NotGround(EffectGround):
    def __init__(self, effect: fondpddl.condition.GroundVar, problem: Problem):
        self.__effect = (AtomDict([]), next(effect.get_effects(problem))[0])

    def is_conditional(self):
        return False

    def get_effects(self, problem: Problem, state: State=None):
        yield self.__effect


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

    def ground(self, problem: Problem):
        return OneOfGround([effect.ground(problem) for effect in self.effects], problem)

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

class OneOfGround(EffectGround):
    def __init__(self, effects: List[EffectGround], problem):
        self.__effects = []
        self.__conditional = []
        for effect in effects:
            if not effect.is_conditional():
                self.__effects += list(effect.get_effects(problem))
            else:
                self.__conditional.append(effect)

    def is_conditional(self):
        return len(self.__conditional) > 0

    def get_effects(self, problem: Problem, state: State=None):
        assert not self.is_conditional() or (state != None and problem != None)
        for effect in self.__effects:
            yield effect
        for conditional in self.__conditional:
            for effect in conditional.get_effects(problem, state):
                yield effect

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

    def ground(self, problem:Problem):
        return WhenGround(self.condition, self.effect.ground(problem), problem)

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

class WhenGround(EffectGround):
    def __init__(self, condition: fondpddl.condition.Precondition, effect: EffectGround, problem:Problem):
        self.condition = condition
        self.__effects = None
        self.__conditional = None
        if not effect.is_conditional():
            self.__effects = list(effect.get_effects(problem))
        else:
            self.__conditional = effect
    
    def is_conditional(self):
        return True

    def get_effects(self, problem: Problem, state: State=None):
        if self.condition.evaluate(state, problem):
            if self.__effects != None:
                for effect in self.__effects:
                    yield effect
                return
            for effect in self.__conditional.get_effects(problem, state):
                yield effect
        else:
            yield AtomDict([]), AtomDict([])
        
