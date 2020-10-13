from fondpddl.condition import Condition

class Not:
    def __init__(self, condition: Condition):
        self.condition = condition