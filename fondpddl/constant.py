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