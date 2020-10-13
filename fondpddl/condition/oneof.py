from fondpddl.condition import Effect
from typing import List

class OneOf:
    def __init__(self, effects: List[Effect]):
        self.effects = effects
