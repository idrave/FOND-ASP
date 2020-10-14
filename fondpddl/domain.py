from fondpddl import ConstType, Constant, Predicate
from fondpddl.action import Action
from typing import List, Optional
import typing


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

        type_set = set(self.types)
        self.by_type = {t:[] for t in type_set}
        for const in self.constants:
            if const.ctype not in type_set:
                raise ValueError(f'Type {const.ctype} of constant {const.name} not declared') 
            self.by_type[const.ctype].append(const)
        
    def get_constants(self, ctype:ConstType=None) -> List[Constant]:
        if ctype == None:
            return self.constants
        return self.by_type.get(ctype, [])
