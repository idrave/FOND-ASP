from __future__ import annotations
from fondpddl import ConstType
from abc import ABC, abstractmethod

class TypedObject(ABC):
    def __init__(self, name: str, ctype: ConstType):
        self.name = name
        self.ctype = ctype
    
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