from __future__ import annotations
class AtomSet:
    def __init__(self, positive=None, negative=None):
        positive = positive if positive != None else set()
        negative = negative if negative != None else set()
        if not isinstance(positive, set):
            positive = set(positive)
        if not isinstance(negative, set):
            negative = set(negative)
        self.intersect = positive & negative
        self.positive = positive.difference(self.intersect)
        self.negative = negative.difference(self.intersect)
    
    @classmethod
    def from_atomset(cls, atoms: AtomSet)-> AtomSet:
        newset = cls()
        newset.intersect = atoms.intersect
        newset.positive = atoms.positive
        newset.negative = atoms.negative
        return newset

    def add_positive(self, positive):
        if positive in self.intersect:
            return
        if positive in self.negative:
            self.negative.remove(positive)
            self.intersect.add(positive)
            return
        self.positive.add(positive)
    
    def add_negative(self, negative):
        if negative in self.intersect:
            return
        if negative in self.positive:
            self.positive.remove(negative)
            self.intersect.add(negative)
            return
        self.negative.add(negative)

    #TODO: do more efficient join
    def join(self, other: AtomSet) -> AtomSet:
        positives = self.positive | self.intersect | other.positive | other.intersect
        negatives = self.negative | self.intersect | other.negative | other.intersect
        newset = AtomSet(positive=positives, negative=negatives)
        return newset


