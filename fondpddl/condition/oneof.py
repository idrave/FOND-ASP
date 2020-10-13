from fondpddl.condition import Condition
from typing import List

class OneOf(Condition):
    def __init__(self, conditions: List[Condition]):
        self.conditions = conditions
