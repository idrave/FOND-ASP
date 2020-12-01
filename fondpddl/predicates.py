from fondpddl import ConstType
from fondpddl.utils import Index
from typing import List

class Predicate:
    def __init__(self, name: str, arguments:List[ConstType]):
        self.name = name
        self.arguments = arguments

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def __str__(self):
        return self.name + '(' + ','.join(map(str, self.arguments)) + ')'

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.name == other.name