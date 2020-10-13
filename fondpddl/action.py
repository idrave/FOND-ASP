from fondpddl.condition import Condition
from fondpddl import Argument
from typing import List

class Action:
    def __init__(self, name: str, parameters: List[Argument],
                 precondition: Condition, effect: Condition):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect