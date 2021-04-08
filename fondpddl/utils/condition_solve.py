import fondpddl
from typing import List


class ConstantSelect:
    def __init__(self, postitions):
        self.__positions = postitions
    def get_positions(self):
        return self.__positions
    def is_negative(self):
        raise NotImplementedError
    def has(self, pos):
        return pos in self.__positions
    def get(self, pos, bounds):
        raise NotImplementedError

class AlwaysTrue(ConstantSelect):
    def __init__(self):
        super().__init__(set())

    def get(self, pos, bounds, val):
        return None, None

class AlwaysFalse(ConstantSelect):
    def __init__(self):
        super().__init__(set())

    def get(self, pos, bounds, val):
        return set(), None

class Conjunction(ConstantSelect):
    def __init__(self, constraints):
        self.__constraints = constraints
        positions = set()
        for c in self.__constraints:
            positions = positions.union(c.get_positions())
        super().__init__(positions)

    def get(self, pos, bounds, val):
        if pos == 0:
            bounds = [None] * len(self.__constraints)
        results = [c.get(pos, b, val) for c, b in zip(self.__constraints, bounds)]
        s = None
        for const, _ in results:
            if const != None:
                if s == None:
                    s = const
                else:
                    s = s.intersection(const)
        return s, [b for _, b in results]

class Disjunction(ConstantSelect):
    def __init__(self, constraints: List[ConstantSelect]):
        self.__constraints = constraints
        positions = set()
        for c in self.__constraints:
            positions = positions.union(c.get_positions())
        super().__init__(positions)

    def get(self, pos, bounds, val):
        if pos == 0:
            bounds = [None] * len(self.__constraints)
        results = [c.get(pos, b, val) for c, b in zip(self.__constraints, bounds)]
        s = set()
        for const, _ in results:
            if const == None:
                return None, [b for _, b in results]
            s = s.union(const)
        return s, [b for _, b in results]


class Negation(ConstantSelect):
    def __init__(self, constraint:ConstantSelect, action, problem):
        self.__constraint = constraint
        self.__last = max(constraint.get_positions().union({-1}))
        if self.__last == -1:
            self.__last_params = None
        else:
            self.__last_params = {c.id for c in problem.get_constants(action.parameters[self.__last].ctype)}
        super().__init__(constraint.get_positions())

    def get(self, pos, bounds, val):
        consts, bounds = self.__constraint.get(pos, bounds, val)
        if pos == self.__last:
            assert consts != None
            return self.__last_params.difference(consts), bounds
        if consts != None and len(consts) == 0:
            return None, bounds
        elif pos > self.__last:
            return set(), bounds
        return None, bounds

class BasicSet(ConstantSelect):
    def __init__(self, postitions, constants):
        super().__init__(postitions)
        self.__constants = constants

    def get(self, pos, bounds, val):
        if pos == 0:
            bounds = (0, len(self.__constants))
            if len(self.__constants) == 0 and len(self.get_positions()) != 0:
                return set(), None
        else:
            if bounds == None or (self.has(pos-1) and val not in bounds):
                return set(), None
            if self.has(pos-1):
                bounds = bounds[val]
        if not self.has(pos):
            return None, bounds
        left, right = bounds
        prev = self.__constants[left][pos]
        prev_left = left
        next_bounds = {}
        
        for i in range(left, right):
            if prev != self.__constants[i][pos]:
                assert prev not in next_bounds
                next_bounds[prev] = (prev_left, i)
                prev = self.__constants[i][pos]
                prev_left = i
        next_bounds[prev] = (prev_left, right)
        return set(next_bounds.keys()), next_bounds


class VariableSet(BasicSet):
    def __init__(self, action,
                       variable,
                       state,
                       problem):
        check_const = [(i, const.get_constant()) for i, const in enumerate(variable.constants) if const.is_ground()]
        constants = []
        pos = {const.get_pos() for const in variable.constants if const.is_act_param()}
        for var_id in state.get_atoms(variable.predicate):
            valid = True
            gvar = problem.get_variable(variable.predicate.get_id(), var_id)
            gvar_constants = gvar.get_const_ids()
            for i, const in check_const:
                if const.id != gvar_constants[i]:
                    valid = False
                    break
            if valid:
                l = [None] * len(action.parameters)
                for const, id in zip(variable.constants, gvar_constants):
                    if const.is_act_param():
                        assert isinstance(const, fondpddl.argument.ActionParam)
                        l[const.get_pos()] = id
                constants.append(tuple(l))
        constants.sort()
        super().__init__(pos, constants)


class EqualitySet(BasicSet):
    def __init__(self, action,
                       const1, const2,
                       problem):
        constants = []
        objs = set()
        pos = set()
        if const1.is_act_param():
            pos.add(const1.get_pos())
        if const2.is_act_param():
            pos.add(const2.get_pos())
        if const1.ctype != const2.ctype:
            super().__init__(pos, constants)
            return
        if const1.is_ground():
            objs.add(const1.get_constant().id)
        if const2.is_ground():
            objs.add(const2.get_constant().id)
        if len(objs) > 1:
            super().__init__(pos, constants)
            return
        elif len(objs) == 0:
            for o in problem.get_constants(ctype=const1.ctype):
                objs.add(o.id)
        for o in sorted(list(objs)):
            l = [None] * len(action.parameters)
            if const1.is_act_param():
                assert isinstance(const1, fondpddl.argument.ActionParam)
                l[const1.get_pos()] = o
            if const2.is_act_param():
                assert isinstance(const2, fondpddl.argument.ActionParam)
                l[const1.get_pos()] = o
            constants.append(tuple(l))
        super().__init__(pos, constants)