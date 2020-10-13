from __future__ import annotations
from typing import Optional

class ConstType:
    def __init__(self, name: str, super_type: Optional[ConstType]=None):
        self.name = name
        self.super_type = super_type

    def __eq__(self, other):
        if not isinstance(other, ConstType):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)