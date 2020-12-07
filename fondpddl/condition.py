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
from typing import List
import fondpddl.effect

class Precondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def evaluate_static(self, state: State, problem: Problem, positive, negative):
        raise NotImplementedError

    @abstractmethod
    def possible_grounding(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def add_ground_act(self, id, problem: Problem):
        raise NotImplementedError

    @abstractmethod
    def get_ground_act(self, state: State, problem: Problem):
        raise NotImplementedError

    @abstractstaticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types): #TODO bug: called in subclasses without parse method
        prec = {
            'and' : And,
            'not' : Not,
            'or': Or, #TODO add disjunctive precondition requirement
            'forall': ForAll #TODO add universal precondition requirement
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
        self.__ground_acts = set()
        pass

    def __str__(self):
        return '()'

    def add_ground_act(self, id, problem: Problem):
        self.__ground_acts.add(id)

    def get_ground_act(self, state: State, problem: Problem):
        return self.__ground_acts

    def evaluate(self, state: State, problem: Problem):
        return True

    def evaluate_static(self, state: State, problem: Problem, positive, negative):
        return (True,)

    def possible_grounding(self, arguments, objects, atoms, neg_vars, problem: Problem):
        yield objects, neg_vars
        '''for i in len(range(objects)):
            if objects[i] == None:
                if problem.domain.is_typed():
                    objects[i] = problem.get_constants(arguments[i].ctype)
                else:
                    objects[i] = problem.get_constants()

        for comb in get_combinations(objects, [], lambda l,x: l.append(x)):
            yield comb'''

    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        return #TODO is this right?

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
        pddl_tree.iter_elements().assert_end()
        return EmptyCondition()


class And(Precondition):
    def __init__(self, conditions: List[Precondition]):
        self.conditions = conditions
        self.__ground_actions = set()

    def evaluate(self, state: State, problem: problem):
        for condition in self.conditions:
            if not condition.evaluate(state, problem):
                return False
        return True

    def add_ground_act(self, id, problem: Problem):
        self.__ground_actions.add(id)
        for condition in self.conditions:
            condition.add_ground_act(id, problem)

    def get_ground_act(self, state: State, problem: Problem):
        ground_acts = set(self.__ground_actions)
        for condition in self.conditions:
            if len(ground_acts) == 0:
                return ground_acts
            ground_acts = ground_acts.intersection(condition.get_ground_act(state, problem))
        return ground_acts

    def evaluate_static(self, state: State, problem: Problem, positive, negative):
        f = False
        for condition in self.conditions:
            cond_vals = condition.evaluate_static(state, problem, positive, negative)
            if (False in cond_vals):
                f = True
                if not (True in cond_vals):
                    return (False, )
        return (True, False) if f else (True,)

    def __possible_grounding(self, arguments, objects, atoms, neg_vars, problem: Problem, i):
        if i == len(self.conditions):
            yield objects, neg_vars
            return
        for g, g_ns in self.conditions[i].possible_grounding(arguments, objects, atoms, neg_vars, problem):
            for objs, ns in self.__possible_grounding(arguments, g, atoms, g_ns, problem, i+1):
                yield objs, ns

    def possible_grounding(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for objs, ns in self.__possible_grounding(arguments, objects, atoms, neg_vars, problem, 0):
            yield objs, ns

    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for condition in self.conditions:
            for objs, ns in condition.make_false(arguments, objects, atoms, neg_vars, problem):
                yield objs, ns

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
        self.__ground_acts = set()

    def add_ground_act(self, id, problem: Problem):
        self.__ground_acts.add(id)
        self.condition.add_ground_act(id, problem)

    def get_ground_act(self, state: State, problem: Problem):
        return self.__ground_acts.difference(self.condition.get_ground_act(state, problem))

    def evaluate(self, state: State, problem: Problem):
        return not self.condition.evaluate(state, problem)

    def evaluate_static(self, state: State, problem: Problem, positive, negative):
        vals = self.condition.evaluate_static(state, problem, positive, negative)
        res = []
        if True in vals:
            res.append(False)
        if False in vals:
            res.append(True)
        return tuple(res)

    def possible_grounding(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for objs, ns in self.condition.make_false(arguments, objects, atoms, neg_vars, problem):
            yield objs, ns

    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for objs, ns in self.condition.possible_grounding(arguments, objects, atoms, neg_vars, problem):
            yield objs, ns

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

    def add_ground_act(self, id, problem: Problem):
        for condition in self.conditions:
            condition.add_ground_act(id, problem)

    def get_ground_act(self, state: State, problem: Problem):
        ground_act = set()
        for condition in self.conditions:
            ground_act = ground_act.union(condition.get_ground_act(state, problem))
        return ground_act

    def evaluate_static(self, state: State, problem: Problem, positive, negative):
        t = False
        for condition in self.conditions:
            cond_vals = condition.evaluate_static(state, problem, positive, negative)
            if (True in cond_vals):
                t = True
                if not (False in cond_vals):
                    return (True,)
        return (True, False) if t else (False,)

    def possible_grounding(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for condition in self.conditions:
            for objs, ns in condition.possible_grounding(arguments, objects, atoms, neg_vars, problem):
                yield objs, ns

    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        conjunction = And([Not(cond) for cond in self.conditions])
        for objs, ns in conjunction.possible_grounding(arguments, objects, atoms, neg_vars, problem):
            yield objs, ns

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
                print(const.name, const.ctype.name)
                raise ValueError(f'Wrong argument type {const.ctype} for {predicate.name}')
        self.__ground_map = {}
    
    def __str__(self):
        return self.predicate.name+'('+','.join([const.name for const in self.constants])+')'

    def add_ground_act(self, id, problem: Problem):
        var_id = self.ground(problem).get_id()
        if var_id not in self.__ground_map:
            self.__ground_map[var_id] = set()
        self.__ground_map[var_id].add(id)

    def get_ground_act(self, state: State, problem: Problem):
        ground_acts = set()
        check_const = [(i, const) for i, const in enumerate(self.constants) if const.is_ground()]
        pred_id = self.predicate.get_id()
        for var_id in state.get_atoms(self.predicate):
            valid = True
            for i, const in check_const:
                gvar = problem.get_variable(pred_id, var_id)
                if const.get_constant().id != gvar.constants[i].id:
                    valid = False
                    break
            if valid:
                ground_acts = ground_acts.union(self.__ground_map.get((pred_id, var_id), set()))
        return ground_acts

    def ground(self, problem: Problem):
        g = GroundVar(self)
        g.set_id(problem)
        return g

    def evaluate(self, state: State, problem: Problem):
        return state.get_value(self.ground(problem))

    def evaluate_static(self, state, problem, positive, negative):
        if self.evaluate(state, problem):
            if self.predicate in negative:
                return (True, False)
            else:
                return (True,)
        else:
            if self.predicate in positive:
                return (True, False)
            else:
                return (False,)

    def get_effects(self, state: State, problem: Problem):
        yield AtomSet(positive=[problem.get_variable_index(self)])

    def get_predicates(self):
        return {self.predicate}, set()

    def possible_grounding(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for values in atoms.get_atoms(self.predicate):
            objs = list(objects)
            valid = True
            for param, obj_id in zip(self.constants, values):
                obj = problem.get_constant(obj_id)
                if param.is_act_param(): #TODO
                    p_pos = param.get_pos()
                    if param.is_ground() and param.get_constant() != obj or \
                            objs[p_pos] != None and objs[p_pos] != obj:
                        valid = False
                        break
                    objs[p_pos] = obj #TODO implement get_pos and predicate and object ids :(
                else:
                    if param.get_constant() != obj:
                        valid = False
                        break
            if not valid:
                continue
            yield objs, neg_vars

    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        n_vars = list(neg_vars)
        params = [(p if not p.is_ground() else p.get_constant()) for p in self.constants] #TODO check if grounded correctly
        Variable(self.predicate, params)
        n_vars.append(self)
        yield objects, n_vars

    @staticmethod
    def parse(pddl_tree: PddlTree, objects, predicates, types):
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

    def add_ground_act(self, id, problem: Problem):
        for constant in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(constant)
            self.condition.add_ground_act(id, problem)
            self.argument.reset()

    def get_ground_act(self, state: State, problem: Problem):
        ground_acts = set()
        for constant in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(constant)
            ground_acts = ground_acts.union(self.condition.get_ground_act(state, problem))
            self.argument.reset()
        return ground_acts

    def evaluate_static(self, state: State, problem: Problem, positive, negative):
        f = False
        for constant in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(constant)
            cond_vals = self.condition.evaluate_static(state, problem, positive, negative)
            if (False in cond_vals):
                f = True
                if not (True in cond_vals):
                    return (False, )
            self.argument.reset()
        return (True, False) if f else (True,)

    def __possible_grounding(self, arguments, objects, atoms, neg_vars, problem: Problem, i, consts):
        if i == len(consts):
            yield objects, neg_vars
        self.argument.ground(consts[i])
        for g, g_ns in self.condition.possible_grounding(arguments, objects, atoms, neg_vars, problem):
            for objs, ns in self.__possible_grounding(arguments, g, atoms, g_ns, problem, i+1, consts):
                yield objs, ns

    def possible_grounding(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for objs, ns in self.__possible_grounding(arguments, objects, atoms, neg_vars, problem,
                                    0, problem.get_constants(ctype=self.argument.ctype)):
            yield objs, ns
        self.argument.reset()

    def make_false(self, arguments, objects, atoms: AtomDict, neg_vars, problem: Problem):
        for const in problem.get_constants(ctype=self.argument.ctype):
            self.argument.ground(const)
            for objs, ns in self.condition.make_false(arguments, objects, atoms, neg_vars, problem):
                yield objs, ns
            self.argument.reset()

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