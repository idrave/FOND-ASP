from __future__ import annotations
from fondpddl import ConstType
from abc import ABC, abstractmethod
from fondpddl.utils.tokens import PddlIter, parse_typed_list

class TypedObject(ABC):
    def __init__(self, name: str, ctype: ConstType):
        self.name = name
        self.ctype = ctype
    
    def __str__(self):
        return self.name

    def has_type(self, ctype: ConstType):
        return self.ctype.is_subtype(ctype)

    @abstractmethod
    def get_constant(self) -> Constant:
        raise NotImplementedError

class Constant(TypedObject):
    def __init__(self, name: str, ctype: ConstType):
        self.name = name
        self.ctype = ctype

    def get_constant(self) -> Constant:
        return self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Constant):
            return False
        return self.name == other.name

def parse_objects(pddl_iter: PddlIter, types=None):
    if types == None:
        constants = {}
        while pddl_iter.has_next():
            const = pddl_iter.get_name()
            if const in constants:
                raise ValueError(f'Duplicate constant {const}')
            constants[const] = Constant(const, None)
        return list(constants.values())

    constants = {}
    types = {t.name : t for t in types}
    typed_list = parse_typed_list(pddl_iter)
    for const_l, type_name in typed_list:
        type_ = types.get(type_name, None)
        if type_ == None:
            raise ValueError(f'Type {type_name} not declared')
        for name in const_l:
            if name in constants:
                raise ValueError(f'Duplicate constant {name}')
            constants[name] = Constant(name, type_)
    return list(constants.values())