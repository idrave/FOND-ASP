from fondpddl import ConstType
from typing import List

class Predicate:
    def __init__(self, name: str, arguments=List[ConstType]):
        self.name = name
        self.arguments = arguments