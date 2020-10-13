from fondpddl import ConstType, Constant, Predicate, Action
from typing import List, Optional

class Domain:
    def __init__(self, name: str, requirements, constants: List[Constant],
                 predicates: List[Predicate], actions: List[Action], constraints,
                 types: Optional[List[ConstType]]):
        self.name = name
        self.requirements = requirements
        self.types = types
        self.constants = constants
        self.predicates = predicates
        self.actions = actions
        self.contraints = constraints