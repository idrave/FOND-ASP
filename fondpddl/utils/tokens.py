from typing import Iterable
import re
NAME = r'[a-z][a-z0-9_-]*'

class PddlTree:
    def __init__(self, elements):
        self._elements = elements

    def count_elements(self):
        return len(self._elements)

    def iter_elements(self):
        return PddlIter(self._elements)

    def __str__(self):
        return '(' + ' '.join(map(str, self._elements)) + ')'

    @staticmethod
    def from_pddl(filename):#TODO add argument
        with open(filename, 'r') as fp:
            pddl = fp.read()
        pddl = re.sub(r';.*', '', pddl)
        pddl = re.sub(r'(\(|\))', r' \1 ', pddl)
        pddl = re.sub(r'\s+', ' ', pddl)
        pddl = pddl.lower()
        token_list = pddl.split()
        def get_elements(index):
            elems = []
            while index < len(token_list) and token_list[index] != ')':
                if token_list[index] == '(':
                    next_index, elem = get_elements(index+1)
                    if next_index == len(token_list):
                        raise ValueError('Unmatched \'(\'')
                    elems.append(elem)
                    index = next_index
                else:
                    elems.append(token_list[index])
                index += 1
            return index, PddlTree(elems)
        last_index, tree = get_elements(0)
        if last_index != len(token_list):
            raise ValueError('Unexpected \')\'')
        return tree
                

class PddlIter:
    def __init__(self, tokens):
        self._tokens = tokens
        self._i = -1

    def has_next(self):
        return self._i + 1 < len(self._tokens)

    def peek(self):
        return self._tokens[self._i + 1] if self.has_next() else None

    def get_next(self):
        self._i += 1
        if self._i < len(self._tokens):
            return self._tokens[self._i]
        return None

    def is_next(self, string):
        return self.has_next() and self.peek() == string

    def assert_token(self, expected):
        token = self.get_next()
        if token != expected:
            raise ValueError(f'Expected {expected}, but got {token}')

    def is_next_name(self):
        return self.has_next() and re.fullmatch(NAME, self.peek()) != None

    def get_name(self):
        token = self.get_next()
        if token == None or re.fullmatch(NAME, token) == None:
            raise ValueError(f'Invalid name {token}')
        return token

    def get_param(self):
        token = self.get_next()
        if token == None or re.fullmatch(r'\?'+NAME, token) == None:
            raise ValueError(f'Invalid name {token}')
        return token

    def is_next_group(self):
        return self.has_next() and isinstance(self.peek(), PddlTree)

    def get_group(self):
        token = self.get_next()
        if token == None or not isinstance(token, PddlTree):
            raise ValueError(f'Unexpected {token}')
        return token

    def assert_end(self):
        if self.has_next():
            raise ValueError(f'Unexpected {self.get_next()}')
        return


def parse_typed_list(pddl_iter: PddlIter, ground=True):
    current = []
    result = []
    while pddl_iter.has_next():
        if not len(current) == 0:
            if pddl_iter.is_next('-'):
                pddl_iter.get_next()
                result.append((current, pddl_iter.get_name()))
                current = []
                continue
        if ground:
            current.append(pddl_iter.get_name())
        else:
            current.append(pddl_iter.get_param())
    result.append((current, 'object'))
    return result