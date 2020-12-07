from fondpddl import Domain, Constant, ConstType, GroundAction, State
import fondpddl.condition
from fondpddl.action import ProblemAction
from fondpddl.condition import Variable, GroundVar, Precondition, EmptyCondition
from fondpddl.effect import AndEffect, Init, EmptyEffect, Effect
from fondpddl.constant import parse_objects
from fondpddl.utils import Index, get_combinations, StaticBitSet
from fondpddl.utils.atomdict import StaticAtomDict
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

        self.var_index = {pred.get_id(): Index() for pred in self.domain.predicates}
        if domain.is_typed():
            self.by_type = domain.by_type
            for const in self.objects:
                if const.ctype not in self.by_type:
                    raise ValueError(f'Type {const.ctype} of constant {const.name} not declared') 
                self.by_type[const.ctype].append(const)

        self.__positive = set()
        self.__negative = set()
        for action in self.domain.actions:
            pos, neg = action.effect.get_predicates()
            self.__positive.update(pos)
            self.__negative.update(neg)
        
        self.__prob_actions = [ProblemAction(action, self) for action in self.domain.actions]
        print(len(self.__prob_actions))

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

    def get_constant(self, c_id):
        return self.objects[c_id]

    def get_variable_index(self, variable: GroundVar):
        id = self.var_index[variable.predicate.get_id()].get_index(variable)
        return id

    def ground_actions(self) -> Generator[GroundAction, None, None]:
        for action in self.domain.actions:
            valid_params = []
            for param in action.parameters:
                valid_params.append(self.get_constants(param.ctype))
            for params in get_combinations(valid_params, [], lambda l,x: l + [x]):
                ground_act = action.ground(params)
                assert isinstance(ground_act, GroundAction)
                yield ground_act

    def get_pos_neg_preds(self):
        '''
        Returns predicates for which some action's effect might change a ground atom
        of such predicate to true or to false.
        '''
        return self.__positive, self.__negative

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
        init = AndEffect(self.init)
        for effects, _ in init.ground(self).get_effects(self, StaticAtomDict()):
            yield State.open_state(StaticAtomDict(effects))
    
    def valid_actions(self, state: State) -> Iterator[GroundAction]:
        for action in self.ground_actions():
            if action.is_valid(state, self):
                yield action
    '''def valid_actions(self, state: State) -> Iterator[GroundAction]:
        for action in self.__prob_actions:
            for ground_act in action.get_valid_actions(state):
                yield ground_act'''
    '''
    def valid_actions(self, state: State) -> Iterator[GroundAction]:
        atom_dict = state.get_atom_dict(self)
        for action in self.domain.actions:
            for g_action in action.valid_ground_actions(atom_dict, self):
                #if g_action.is_valid(state, self):
                    yield g_action'''

    def apply_action(self, state: State, action: GroundAction)-> Iterator[State]:
        for positive, negative in action.get_effects(state, self):
            st = state.change_values(positive, negative)
            yield st

    def is_goal(self, state: State)->bool:
        return self.goal.evaluate(state, self)

    def get_variable(self, pred_id, var_id):
        return self.var_index[pred_id][var_id]

    def print_variable(self, pred_id, var_id):
        print(str(self.get_variable(pred_id, var_id)))

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
        obj_index = Index(domain.constants)
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':objects')
        if domain.is_typed():
            types = domain.types
        else:
            types = None
        parse_objects(pddl_iter, obj_index, types=types)
        problem_params[PROBLEM_OBJ] = obj_index.elems

    @staticmethod
    def parse_init(pddl_tree: PddlTree, domain: Domain, problem_params):
        if PROBLEM_INIT in problem_params:
            raise ValueError('Redefinition of init')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':init')
        inits = []
        objects = problem_params.get(PROBLEM_OBJ, [])
        objects = {obj.name : obj for obj in objects}
        predicates = {pred.name: pred for pred in domain.predicates}
        if domain.is_typed():
            type_dict = {ty.name: ty for ty in domain.types}
        else:
            type_dict = None
        while pddl_iter.has_next():
            init = Init.parse(pddl_iter.get_group(), objects, predicates, type_dict, toplevel=True)
            inits.append(init)
        problem_params[PROBLEM_INIT] = inits

    @staticmethod
    def parse_goal(pddl_tree: PddlTree, domain: Domain, problem_params):
        if PROBLEM_GOAL in problem_params:
            raise ValueError('Redefinition of goal')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':goal')
        objects = problem_params.get(PROBLEM_OBJ,[])
        objects = {obj.name: obj for obj in objects}
        predicates = {pred.name: pred for pred in domain.predicates}
        if domain.is_typed():
            types = {ty.name: ty for ty in domain.types}
        else:
            types = None
        goal = Precondition.parse(pddl_iter.get_group(), objects, predicates, types)
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
        objects = problem_params.get(PROBLEM_OBJ,[])
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
        objects = problem_params.get(PROBLEM_OBJ,[])
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

    