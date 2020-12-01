from fondpddl import TypedObject, Constant, ConstType
from fondpddl.utils.tokens import parse_typed_list

class Argument(TypedObject):
    def __init__(self, name: str, ctype: ConstType):
        super().__init__(name, ctype)
        self.ground_value = None
    
    def is_ground(self):
        return self.ground_value != None

    def get_constant(self) -> Constant:
        if self.ground_value  == None:
            raise ValueError(f'Argument {self.name} not grounded')
        return self.ground_value

    def ground(self, constant: Constant):
        if self.ctype != None and not constant.has_type(self.ctype):
            raise ValueError(f'Type {self.ctype} expected, but got {constant.ctype}')
        self.ground_value = constant

    def is_act_param(self):
        return False

    def reset(self):
        self.ground_value = None


class ActionParam(Argument):
    def __init__(self, arg: Argument, position):
        super().__init__(arg.name, arg.ctype)
        self.pos = position

    def get_pos(self):
        return self.pos

    def is_act_param(self):
        return True


def parse_parameters(pddl_iter, types=None):
    param_names = set()
    params = []

    if types == None:
        while pddl_iter.has_next():
            param = pddl_iter.get_param()
            if param in param_names:
                raise ValueError(f'Duplicate parameter {param}')
            param_names.add(param)
            params.append(Argument(param, None))
        return params
    
    types = {t.name : t for t in types}
    typed_list = parse_typed_list(pddl_iter, ground=False)
    for param_l, type_name in typed_list:
        type_ = types.get(type_name, None)
        if type_ == None:
            raise ValueError(f'Type {type_name} not declared')
        for name in param_l:
            if name in param_names:
                raise ValueError(f'Duplicate parameter {name}')
            param_names.add(name)
            params.append(Argument(name, type_))
    return params
    
    