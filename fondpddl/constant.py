from __future__ import annotations
from fondpddl import ConstType
from abc import ABC, abstractmethod
from fondpddl.utils import Index
from fondpddl.utils.tokens import PddlIter, parse_typed_list

class TypedObject(ABC):
    def __init__(self, name: str, ctype: ConstType):
        self.name = name
        self.ctype = ctype
    
    def __str__(self):
        return self.name

    def has_type(self, ctype: ConstType):
        return self.ctype.is_subtype(ctype)

    def is_act_param(self):
        raise NotImplementedError

    @abstractmethod
    def get_constant(self) -> Constant:
        raise NotImplementedError

    @abstractmethod
    def is_ground(self):
        raise NotImplementedError


class Constant(TypedObject):
    def __init__(self, name: str, ctype: ConstType):
        self.name = name
        self.ctype = ctype
    
    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def is_ground(self):
        return True

    def get_constant(self) -> Constant:
        return self

    def is_act_param(self):
        return False

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Constant):
            return False
        return self.name == other.name


def parse_objects(pddl_iter: PddlIter, const_index:Index, types=None):
    if types == None:
        while pddl_iter.has_next():
            name = pddl_iter.get_name()
            const = Constant(name, None)
            if const_index.find_index(const) != None:
                raise ValueError(f'Duplicate constant {name}')
            const.set_id(const_index.get_index(const))
        return

    types = {t.name : t for t in types}
    typed_list = parse_typed_list(pddl_iter)
    for const_l, type_name in typed_list:
        type_ = types.get(type_name, None)
        if type_ == None:
            raise ValueError(f'Type {type_name} not declared')
        for name in const_l:
            const = Constant(name, type_)
            if const_index.find_index(const) != None:
                raise ValueError(f'Duplicate constant {name}')
            const.set_id(const_index.get_index(const))