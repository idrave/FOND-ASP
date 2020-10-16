from fondpddl import Domain, Constant, ConstType, GroundAction, State
from fondpddl.condition import Variable, Precondition, Effect, AndEffect
from fondpddl.utils import Index, get_combinations, StaticBitSet
from typing import List, Generator, Iterator, Tuple

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

    def get_constants(self, ctype: ConstType=None) -> List[Constant]:
        if ctype == None:
            return self.objects
        return self.by_type.get(ctype, [])

    def get_variable_index(self, variable: Variable):
        predicate = (self.pred_index[variable.predicate], )
        constants = tuple(self.const_index[const.get_constant()] for const in variable.constants)
        return self.var_index[predicate + constants]

    def ground_actions(self) -> Generator[GroundAction, None, None]:
        for action in self.domain.actions:
            valid_params = []
            for param in action.parameters:
                valid_params.append(self.get_constants(param.ctype))
            #print([[o.name for o in c] for c in valid_params])
            for params in get_combinations(valid_params, [], lambda l,x: l + [x]):
                ground_act = action.ground(params)
                assert isinstance(ground_act, GroundAction)
                yield ground_act
    
    def get_initial_states(self) -> Iterator[State]:
        for effects in AndEffect(self.init).get_effects(State(StaticBitSet), self):
            yield State.from_atomset(effects)

    def valid_actions(self, state: State) -> Iterator[GroundAction]:
        for action in self.ground_actions():
            if action.is_valid(state, self):
                yield action

    def apply_action(self, state: State, action: GroundAction)-> Iterator[State]:
        for effects in action.get_effects(state, self):
            st = state.change_values(effects)
            yield st

    def is_goal(self, state: State)->bool:
        return self.goal.evaluate(state, self)

    def get_variable(self, index):
        var = self.var_index[index]
        pred = self.pred_index[var[0]]
        consts = [self.const_index[c] for c in var[1:]]
        return Variable(pred, consts)

    def print_variable(self, index):
        var = self.var_index[index]
        pred = self.pred_index[var[0]]
        consts = [self.const_index[c] for c in var[1:]]
        print(str(Variable(pred, consts)))