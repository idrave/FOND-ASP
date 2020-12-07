from typing import List, Optional, Hashable

class Index:
    def __init__(self, elems: Optional[List[Hashable]]=None):
        self.elems = list(elems) if elems != None else []
        self.index = {elem: i for elem, i in enumerate(self.elems)}
    
    def __len__(self):
        return len(self.elems)

    def __getitem__(self, index):
        return self.elems[index]

    def __iter__(self):
        self.__it = -1
        return self

    def __next__(self):
        self.__it += 1
        if self.__it < len(self):
            return self[self.__it]
        else:
            raise StopIteration

    def get_index(self, elem: Hashable) -> int:
        ind = self.find_index(elem)
        if ind == None:
            self.index[elem] = len(self.elems)
            ind = len(self.elems)
            self.elems.append(elem)
        return ind

    def find_index(self, elem: Hashable) -> Optional[int]:
        return self.index.get(elem, None)
