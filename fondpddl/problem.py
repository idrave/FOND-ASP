from fondpddl import Domain, Constant
from fondpddl.condition import Variable, Condition
from typing import List

class Problem:
    def __init__(self, name: str, domain: Domain, objects: List[Constant],
                 init: List[Variable], goal: Condition):
        self.name = name
        self.domain = domain
        self.objects = objects
        self.init = init
        self.goal = goal