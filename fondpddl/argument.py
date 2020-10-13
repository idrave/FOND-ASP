from fondpddl import TypedObject, Constant, ConstType

class Argument(TypedObject):
    def __init__(self, name: str, ctype: ConstType):
        super().__init__(name, ctype)
        self.ground_value = None
    
    def get_constant(self) -> Constant:
        return self.ground_value

    def ground(self, constant: Constant):
        if constant.ctype != self.ctype:
            raise ValueError(f'Type {self.ctype} expected, but got {constant.ctype}')
        self.ground_value = constant

    def reset(self):
        self.ground_value = None
    
    
    