from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem
    
from fondpddl.condition import Effect
from typing import List

class OneOf:
    def __init__(self, effects: List[Effect]):
        self.effects = effects

    def get_effects(self, state: State, problem: Problem):
        for effect in self.effects:
            for det_effect in effect.get_effects(state, problem):
                yield det_effect
