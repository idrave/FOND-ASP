from abc import ABC, abstractmethod
from fondpddl import State, Problem
from fondpddl.utils import Index

class Effect:
    def __init__(self):
        pass


class Precondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State, problem: Problem):
        raise NotImplementedError