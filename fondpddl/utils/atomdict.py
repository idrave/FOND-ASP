from __future__ import annotations
from typing import List, Optional
import fondpddl.condition
from fondpddl.utils import BitSet, StaticBitSet
import copy

class IntSet():
    def __init__(self, values):
        self.__array = BitSet()
        self.__set = set()
        for v in values:
            self.add(v)

    def add(self, v):
        self.__array[v] = 1
        self.__set.add(v)

    def remove(self, v):
        self.__array[v] = 0
        self.__set.remove(v)

    def has(self, i):
        return self.__array[i]

    def get_hash(self):
        return hash(StaticBitSet(self.__array))

    def get_all(self):
        return self.__set

    def add_set(self, other: IntSet, inplace=False):
        for v in other:
            self.add(v)

    def is_equal(self, other: IntSet):
        if not isinstance(other, IntSet):
            return False
        return self.get_all() == other.get_all()

    def __iter__(self):
        return iter(self.__set)

    def symmetric_difference(self, other: IntSet):
        self.__set = self.__set ^ other.get_all()


class AtomDict:
    def __init__(self, atoms:Optional[List[fondpddl.condition.GroundVar]]=None):
        atoms = atoms if atoms is not None else []
        self.__sets = {}
        for p in atoms:
            self.add(p)

    def add(self, atom: fondpddl.condition.GroundVar):
        '''
        Add ground variable to AtomDict
        '''
        p_id, v_id = atom.get_id()
        self.add_ids(p_id, v_id)

    def add_ids(self, p_id, v_id):
        '''
        Add ground variable to AtomDict, using predicate id and variable id
        '''
        if p_id not in self.__sets[p_id]:
            self.__sets[p_id] = IntSet([])
        self.__sets[p_id].add(v_id)

    def add_atoms_ids(self, p_id, intset):
        '''
        Add set of ground variables to AtomDict, using predicate id and IntSet with
        ground variable ids
        '''
        if p_id not in self.__sets[p_id]:
            self.__sets[p_id] = IntSet([])
        self.__sets[p_id].add_set(intset)

    def get_atoms(self, predicate):
        '''
        Get ground variables for some predicate in AtomDict
        '''
        p_id = predicate.get_id()
        return self.get_atoms_id(p_id)

    def get_atoms_id(self, p_id):
        '''
        Get ground variables for some predicate in AtomDict, given the predicate id
        '''
        if p_id not in self.__sets:
            raise ValueError(f'AtomDict: no predicate id {p_id} in dictionary')
        return self.__sets[p_id]

    def get_pred_ids(self):
        '''
        Get the ids of predicates stored in the AtomDict
        '''
        return set(self.__sets.keys())

    def has(self, atom):
        '''
        Check if ground variable is contained in AtomDict
        '''
        p_id, v_id = atom.get_id()
        return self.has_ids(p_id, v_id)

    def has_ids(self, p_id, v_id):
        '''
        Check if ground variable is contained in AtomDict,
        using predicate id and ground variable's id
        '''
        return self.__sets[p_id].has(v_id)

    def has_pred_id(self, p_id):
        '''
        Check if predicate id is contained in AtomDict
        '''
        return p_id in self.__sets

    def iter(self):
        '''
        Iterate through predicates' ids in the AtomDict and their corresponding
        IntSets with the ground variables stored
        '''
        for p_id, intset in self.__sets.keys():
            yield p_id, intset

    def iter_ids(self):
        '''
        Iterate through ground variables in the AtomDict, returns predicate and ground variable
        ids for each variable
        '''
        for p_id, intset in self.__sets.keys():
            for v_id in intset:
                yield p_id, v_id

    def get_hash(self):
        return sum([s.get_hash() for s in self.__sets])

    def is_equal(self, atoms):
        if not isinstance(atoms, AtomDict) and not isinstance(atoms, StaticAtomDict):
            return False
        if not self.get_pred_ids() == atoms.get_pred_ids():
            return False
        for p_id, intset in self.iter():
            if not intset.is_equal(atoms.get_atoms_id(p_id)):
                return False
        return True

    def get_static(self):
        return StaticAtomDict(self)

    def join(self, other: AtomDict):
        atoms = copy.deepcopy(self)
        for p_id, intset in other.iter():
            atoms.add_atoms_ids(p_id, intset)
        return atoms

    def symmetric_difference(self, other: AtomDict):
        atoms = copy.deepcopy(self)
        for p_id, intset in other.iter():
            if p_id not in atoms.get_pred_ids():
                atoms.add_atoms_ids(p_id, intset)
            else:
                atoms.get_atoms_id(p_id).symmetric_difference(intset)
        return atoms


class StaticAtomDict():
    def __init__(self, atoms: AtomDict):
        self.__atoms = atoms
        self.__hash = atoms.get_hash()

    def get_atoms(self, predicate):
        return self.__atoms.get_atoms(predicate)

    def has(self, atom):
        return self.__atoms.has(atom)

    def has_ids(self, p_id, v_id):
        return self.__atoms.has_ids(p_id, v_id)

    def iter_ids(self):
        for p_id, v_id in self.__atoms.iter_ids():
            yield p_id, v_id

    def join(self, other: AtomDict):
        return self.__atoms.join(other)

    def __hash__(self):
        return self.__hash

    def __eq__(self, other):
        return self.__atoms.is_equal(other)
