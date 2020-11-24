from fondpddl import Domain, Constant, ConstType, GroundAction, State
import fondpddl.condition
from fondpddl.condition import Variable, Precondition, Effect, AndEffect, Init, EmptyEffect, EmptyCondition
from fondpddl.constant import parse_objects
from fondpddl.utils import Index, get_combinations, StaticBitSet
from fondpddl.utils.tokens import PddlIter, PddlTree
from typing import List, Generator, Iterator, Tuple

PROBLEM_NAME = 'name'
PROBLEM_OBJ = 'objects'
PROBLEM_INIT = 'init'
PROBLEM_GOAL = 'goal'
PROBLEM_FAIR = 'fair'
PROBLEM_QNP = 'constraint'

class Problem:
    def __init__(self, name: str, domain: Domain, objects: List[Constant],
                 init: List[Init], goal: Precondition, fair, constraints):
        self.name = name
        self.domain = domain
        self.objects = objects
        self.init = init
        self.goal = goal
        self.set_fairness(fair, constraints)

        self.pred_index = Index(self.domain.predicates)
        self.const_index = Index(self.get_constants())
        self.var_index = Index()
        if domain.is_typed():
            self.by_type = domain.by_type
            for const in self.objects:
                if const.ctype not in self.by_type:
                    raise ValueError(f'Type {const.ctype} of constant {const.name} not declared') 
                self.by_type[const.ctype].append(const)
        self.__ground_actions = self.possible_ground_actions()

    def set_fairness(self, fair: List[GroundAction],
                     constraints: List[Tuple[List[GroundAction], List[GroundAction]]]):
        self.fair = set(fair)
        self.constraints = constraints
        self.__const_map = {}
        for i, (const_a, const_b) in enumerate(self.constraints):
            for action in const_a:
                if action not in self.__const_map:
                    self.__const_map[action] = ([],[])
                self.__const_map[action][0].append(i)
            for action in const_b:
                if action not in self.__const_map:
                    self.__const_map[action] = ([],[])
                self.__const_map[action][1].append(i)

    def is_strong_cyclic(self, action: GroundAction):
        return action in self.fair

    def get_qnp_constraints(self, action: GroundAction):
        return self.__const_map.get(action, ([], [])) #TODO check if valid action

    def get_constants(self, ctype: ConstType=None) -> List[Constant]:
        if ctype == None:
            return self.objects + self.domain.constants
        return self.by_type.get(ctype, [])

    def get_variable_index(self, variable: Variable):
        predicate = (variable.predicate, )
        constants = tuple(const.get_constant() for const in variable.constants)
        return self.var_index[predicate + constants]

    def ground_actions(self) -> Generator[GroundAction, None, None]:
        for action in self.domain.actions:
            valid_params = []
            for param in action.parameters:
                valid_params.append(self.get_constants(param.ctype))
            for params in get_combinations(valid_params, [], lambda l,x: l + [x]):
                ground_act = action.ground(params)
                assert isinstance(ground_act, GroundAction)
                yield ground_act
    
    def get_ground_actions(self):
        return self.__ground_actions

    def possible_ground_actions(self):
        ground_actions = []
        positive = set()
        negative = set()
        for action in self.domain.actions:
            pos, neg = action.effect.get_predicates()
            positive.update(pos)
            negative.update(neg)
        for gact in self.ground_actions():
            for s0 in self.get_initial_states():
                if gact.is_valid_static(s0, self, positive, negative):
                    ground_actions.append(gact)
        return ground_actions

    def get_initial_states(self) -> Iterator[State]:
        for effects in AndEffect(self.init).get_effects(State(StaticBitSet), self):
            yield State.from_atomset(effects)

    def valid_actions(self, state: State) -> Iterator[GroundAction]:
        #for action in self.ground_actions():
        for action in self.get_ground_actions():
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
        pred = var[0]
        consts = var[1:]
        return Variable(pred, consts)

    def print_variable(self, index):
        print(str(self.get_variable(index)))

    def str_constraints(self):
        constraints = []
        for con_a, con_b in self.constraints:
            constraints.append('(CONSTRAINT\n\t' + ' '.join(map(str, con_a))+ ',\n\t' + \
                                ' '.join(map(str, con_b)) + ')')
        return '\n'.join(constraints)

    def __str__(self):
        return '(PROBLEM ' + self.name + '\nDOMAIN ' + self.domain.name + '\n' + \
            'OBJECTS ' + ' '.join(map(str, self.objects))+'\n' + \
            'INIT (' + ' '.join(map(str, self.init)) + ')\n' + \
            'GOAL (' + str(self.goal) + ')\n' + \
            'FAIR (' + ' '.join(map(str, self.fair)) + ')\n' + \
            self.str_constraints() + ')\n'

    @staticmethod
    def parse_elem(pddl_tree: PddlTree, domain, problem_params):
        methods = {
            ':objects' : Problem.parse_objects,
            ':init' : Problem.parse_init,
            ':goal' : Problem.parse_goal,
            ':fair' : Problem.parse_fair,
            ':constraint' : Problem.parse_constraint
        }
        first_token = pddl_tree.iter_elements().get_next()
        if first_token not in methods:
            raise ValueError(f'Invalid term {first_token}')
        methods[first_token](pddl_tree, domain, problem_params)

    @staticmethod
    def parse(filename, domains):
        pddl_tokens = PddlTree.from_pddl(filename)
        if pddl_tokens.count_elements() < 1:
            raise ValueError('Problem not found')
        token_iter = pddl_tokens.iter_elements()
        problem = Problem.parse_tokens(token_iter.get_group(), domains)
        token_iter.assert_end()
        return problem

    @staticmethod
    def parse_tokens(pddl_tree: PddlTree, domains):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('define')
        problem_params = {}
        name = Problem.parse_name(pddl_iter.get_group())
        problem_params[PROBLEM_NAME] = name
        domain = Problem.parse_domain(pddl_iter.get_group(), domains)
        while pddl_iter.has_next():
            next_elem = pddl_iter.get_group()
            Problem.parse_elem(next_elem, domain, problem_params)
        return Problem(
            name,
            domain,
            problem_params.get(PROBLEM_OBJ, []),
            problem_params.get(PROBLEM_INIT, EmptyEffect()),
            problem_params.get(PROBLEM_GOAL, EmptyCondition()),
            problem_params.get(PROBLEM_FAIR, []),
            problem_params.get(PROBLEM_QNP, [])
        )

    @staticmethod
    def parse_name(pddl_tokens: PddlTree):
        pddl_iter = pddl_tokens.iter_elements()
        pddl_iter.assert_token('problem')
        name = pddl_iter.get_name()
        pddl_iter.assert_end()
        return name

    @staticmethod
    def parse_domain(pddl_tree: PddlTree, domains):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':domain')
        domain_name = pddl_iter.get_name()
        domain = domains.get(domain_name, None)
        if domain == None:
            raise ValueError(f'Domain {domain_name} not defined')
        pddl_iter.assert_end()
        return domain

    @staticmethod
    def parse_objects(pddl_tree: PddlTree, domain: Domain, problem_params):
        if PROBLEM_OBJ in problem_params:
            raise ValueError('Redefinition of objects')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':objects')
        if domain.is_typed():
            types = domain.types
        else:
            types = None
        problem_params[PROBLEM_OBJ] = parse_objects(pddl_iter, types=types) #TODO check duplicate objects

    @staticmethod
    def parse_init(pddl_tree: PddlTree, domain: Domain, problem_params):
        if PROBLEM_INIT in problem_params:
            raise ValueError('Redefinition of init')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':init')
        inits = []
        objects = problem_params.get(PROBLEM_OBJ,[]) + domain.constants
        objects = {obj.name : obj for obj in objects}
        predicates = {pred.name: pred for pred in domain.predicates}
        while pddl_iter.has_next():
            init = Init.parse(pddl_iter.get_group(), objects, predicates, toplevel=True)
            inits.append(init)
        problem_params[PROBLEM_INIT] = inits

    @staticmethod
    def parse_goal(pddl_tree: PddlTree, domain: Domain, problem_params):
        if PROBLEM_GOAL in problem_params:
            raise ValueError('Redefinition of goal')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':goal')
        objects = problem_params.get(PROBLEM_OBJ,[]) + domain.constants
        objects = {obj.name: obj for obj in objects}
        predicates = {pred.name: pred for pred in domain.predicates}
        goal = Precondition.parse(pddl_iter.get_group(), objects, predicates)
        pddl_iter.assert_end()
        problem_params[PROBLEM_GOAL] = goal

    @staticmethod
    def parse_fair(pddl_tree: PddlTree, domain: Domain, problem_params):
        if PROBLEM_FAIR in problem_params:
            raise ValueError('Redefinition of fair action set')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':fair')
        g_actions = []
        actions = domain.actions
        objects = problem_params.get(PROBLEM_OBJ,[]) + domain.constants
        while pddl_iter.has_next():
            action = GroundAction.parse(pddl_iter.get_group(), actions, objects)
            if PROBLEM_QNP in problem_params:
                constraints = problem_params[PROBLEM_QNP]
                if any(action in a+b for a, b in constraints):
                    raise ValueError(f'Action {str(action)} already has different fariness type')
            g_actions.append(action)
        problem_params[PROBLEM_FAIR] = g_actions

    @staticmethod
    def parse_constraint(pddl_tree: PddlTree, domain: Domain, problem_params):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':constraint')
        actions = domain.actions
        objects = problem_params.get(PROBLEM_OBJ,[]) + domain.constants
        a = None
        b = None
        while pddl_iter.has_next():
            if pddl_iter.is_next(':a'):
                if a != None:
                    raise ValueError() #TODO
                a = []
                act_list = a
            elif pddl_iter.is_next(':b'):
                if b != None:
                    raise ValueError() #TODO
                b = []
                act_list = b
            else:
                raise ValueError(f'Unexpected {pddl_iter.get_next()} in constraint definition')
            pddl_iter.get_next()
            #act_iter = pddl_iter.get_group().iter_elements()
            while pddl_iter.is_next_group():
                action = GroundAction.parse(pddl_iter.get_group(), actions, objects)
                if PROBLEM_FAIR in problem_params:
                    if action in problem_params[PROBLEM_FAIR]:
                        raise ValueError(f'Action {str(action)} already has different fariness type')
                act_list.append(action)
        if PROBLEM_QNP not in problem_params:
            problem_params[PROBLEM_QNP] = []
        problem_params[PROBLEM_QNP].append((a if a != None else [], b if b != None else []))

    