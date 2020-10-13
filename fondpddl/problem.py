from fondpddl import Domain, Constant, ConstType, GroundAction
from fondpddl.condition import Variable, Precondition, Effect
from fondpddl.utils import Index
from typing import List, Generator

#TODO: is Effect appropriate for init argument?
class Problem:
    def __init__(self, name: str, domain: Domain, objects: List[Constant],
                 init: List[Effect], goal: Precondition):
        self.name = name
        self.domain = domain
        self.objects = objects
        self.init = init
        self.goal = goal

        self.pred_index = Index(self.domain.predicates)
        self.const_index = Index(self.domain.constants + self.objects)
        self.var_index = Index()

        self.by_type = domain.by_type
        for const in self.objects:
            if const.ctype not in self.by_type:
                raise ValueError(f'Type {const.ctype} of constant {const.name} not declared') 
            self.by_type[const.ctype].append(const)

    def get_constants(self, ctype:ConstType=None) -> List[Constant]:
        if ctype == None:
            return self.objects
        return self.by_type.get(ctype, [])

    def get_variable_index(self, variable: Variable):
        predicate = (self.pred_index[variable.predicate], )
        constants = (self.const_index[const] for const in variable.constants)
        return self.var_index[predicate + constants]

    def ground_actions(self) -> Generator[GroundAction, None, None]:

        def get_combinations(options: List[List], current=[]):
            if len(current) == len(options):
                yield current
            else:
                i = len(current)
                for op in options[i]:
                    for comb in get_combinations(options, current + [op]):
                        yield comb

        for action in self.domain.actions:
            valid_params = []
            for param in action.parameters:
                valid_params.append(self.get_constants(param.ctype))
            for params in get_combinations(valid_params):
                ground_act = action.ground(params)
                assert isinstance(ground_act, GroundAction)
                yield ground_act
           

