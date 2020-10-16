from abc import ABC, abstractmethod
from typing import Iterator
from fondpddl import State

class GraphIterator(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def iterate(self, problem, expand_goal)->Iterator[State]:
        raise NotImplementedError