from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from fondpddl.state import State
    from fondpddl import Problem

from abc import ABC, abstractmethod
from fondpddl.utils import Index



class Effect(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_effects(self, state: State, problem: Problem):
        raise NotImplementedError


class Precondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State, problem: Problem):
        raise NotImplementedError