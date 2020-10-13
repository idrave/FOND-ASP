from fondpddl import Predicate, Constant
from fondpddl.condition import Condition
from typing import List

class Variable(Condition):
    def __init__(self, predicate: Predicate, constants: List[Constant]):
        self.predicate = predicate
        self.constants = constants