from __future__ import annotations
from typing import Optional, List
from collections import deque
class ConstType:
    def __init__(self, name: str, super_types: Optional[List[ConstType]]=None):
        self.name = name
        self.super_types = super_types
        self.__all_super = None

    def is_subtype(self, ctype: ConstType):
        return self == ctype or ctype in self.get_all_super_types()

    def get_super_types(self):
        """Returns direct super types of this ()"""
        return self.super_types

    def get_all_super_types(self):
        if self.__all_super is None:
            q = deque([self])
            visited = set()
            while len(q):
                x = q.pop()
                visited.add(x)
                for y in x.get_super_types():
                    if y not in visited: q.append(y)
            visited.remove(self)
            self.__all_super = visited
        return self.__all_super

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, ConstType):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)