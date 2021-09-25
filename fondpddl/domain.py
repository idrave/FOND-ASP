from re import T
from fondpddl import ConstType, Constant, Predicate, Argument
from fondpddl.utils import Index
from fondpddl.utils.tokens import PddlTree, PddlIter, parse_typed_list
from fondpddl.constant import parse_objects
from fondpddl.argument import parse_parameters
from fondpddl.action import Action
from typing import List, Optional


class Requirements:
    def __init__(self, requirements):
        self.__requirements = requirements
        self.__typing = ':typing' in requirements

    def has_typing(self):
        return self.__typing

    def __str__(self):
        return 'REQUIREMENTS ' + ' '.join(self.__requirements)

    @staticmethod
    def parse_requirements(pddl_iter: PddlIter):
        req = []
        while pddl_iter.has_next():
            req.append(pddl_iter.get_next()) #TODO check requirement format
        return Requirements(req)


DOMAIN_NAME = 'name'
DOMAIN_REQ = 'requirements'
DOMAIN_CONST = 'constants'
DOMAIN_PRED = 'predicates'
DOMAIN_ACT = 'actions'
DOMAIN_TYP = 'types'
IS_TYPE_SET = 'istypeset'

class Domain:
    def __init__(self, name: str, requirements: Requirements, constants: List[Constant],
                 predicates: List[Predicate], actions: List[Action], constraints,
                 types: Optional[List[ConstType]]= None):
        self.set_name(name)
        self.set_requirements(requirements)
        self.constants = []
        self.types = None
        if types != None:
            self.set_types(types)
        self.set_constants(constants)
        self.set_predicates(predicates)
        self.set_actions(actions)
        self.constraints = constraints #TODO add constraints inside actions

    def __str__(self):
        return '(DOMAIN ' + self.name + '\n' + str(self.requirements) + '\n' + \
            (('TYPES ' + ' '.join(map(str, self.types))+'\n') if self.is_typed() else '') + \
            'CONSTANTS (' + ' '.join(map(str, self.constants)) + ')\n' + \
            'PREDICATES (' + ' '.join(map(str, self.predicates)) + ')\n' + \
            '\n'.join(map(str, self.actions)) + '\n'
            

    def set_name(self, name):
        self.name = name

    def set_requirements(self, requirements):
        self.requirements = requirements

    def is_typed(self):
        return self.requirements.has_typing()

    def set_constants(self, constants):
        self.constants = constants
        if self.is_typed():
            self._create_by_type()

    def set_types(self, types):
        self.types = types #TODO check requirements
        self._create_by_type()

    def set_predicates(self, predicates):
        self.predicates = predicates
        #self._validate_predicates() TODO

    def set_actions(self, actions):
        self.actions = actions
        #self._validate_actions() TODO

    def _create_by_type(self):
        type_set = set(self.types)
        self.by_type = {t:[] for t in type_set}
        for const in self.constants:
            if const.ctype not in type_set:
                raise ValueError(f'Type {const.ctype} of constant {const.name} not declared')
            t = const.ctype
            while t != None:
                self.by_type[t].append(const)
                t = t.super_type

    def get_constants(self, ctype:ConstType=None) -> List[Constant]: #TODO implement subtype usage
        if ctype == None:
            return self.constants
        return self.by_type.get(ctype, [])

    @staticmethod
    def parse(filename):
        pddl_tokens = PddlTree.from_pddl(filename)
        if pddl_tokens.count_elements() < 1:
            raise ValueError('Domain not found')
        token_iter = pddl_tokens.iter_elements()
        domain = Domain.parse_tokens(token_iter.get_group())
        token_iter.assert_end()
        return domain
    
    @staticmethod
    def parse_tokens(pddl_tree: PddlTree):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token('define')
        domain_params = {IS_TYPE_SET: False}
        name = Domain.parse_name(pddl_iter.get_group())
        domain_params[DOMAIN_NAME] = name
        while pddl_iter.has_next():
            next_elem = pddl_iter.get_group()
            Domain.parse_elem(next_elem, domain_params)
        typed = DOMAIN_REQ in domain_params and domain_params[DOMAIN_REQ].has_typing()
        return Domain(
            name, domain_params.get(DOMAIN_REQ, Requirements([])),
            domain_params.get(DOMAIN_CONST, []),
            domain_params.get(DOMAIN_PRED, []),
            domain_params.get(DOMAIN_ACT, []), [],
            domain_params[DOMAIN_TYP] if typed else None
        )

    @staticmethod
    def parse_name(pddl_tokens: PddlTree):
        pddl_iter = pddl_tokens.iter_elements()
        pddl_iter.assert_token('domain')
        name = pddl_iter.get_name()
        pddl_iter.assert_end()
        return name

    @staticmethod
    def parse_elem(pddl_tree: PddlTree, domain_params):
        methods = {
            ':requirements' : Domain.parse_requirements,
            ':types' : Domain.parse_types,
            ':constants' : Domain.parse_constants,
            ':predicates' : Domain.parse_predicates,
            ':action' : Domain.parse_action
        }
        first_token = pddl_tree.iter_elements().get_next()
        if first_token not in methods:
            raise ValueError(f'Invalid term {first_token}')
        methods[first_token](pddl_tree, domain_params)

    @staticmethod
    def parse_requirements(pddl_tree: PddlTree, domain_params):
        if DOMAIN_REQ in domain_params:
            raise ValueError('Redefinition of requirements')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':requirements')
        domain_params[DOMAIN_REQ] = Requirements.parse_requirements(pddl_iter)
        if domain_params[DOMAIN_REQ].has_typing():
            domain_params[DOMAIN_TYP] = [ConstType('object')]
        else:
            domain_params[DOMAIN_TYP] = None

    @staticmethod
    def parse_types(pddl_tree: PddlTree, domain_params):
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':types')
        if not domain_params[DOMAIN_REQ].has_typing():
            raise ValueError(':typing requirement missing using types')
        if domain_params[IS_TYPE_SET]:
            raise ValueError('Redefinition of types')
        typed_list = parse_typed_list(pddl_iter)
        types = {"object": None}
        for type_l, super_type_name in typed_list:
            for name in type_l:
                if name in types:
                    raise ValueError(f'Duplicate type {name}')
                types[name] = super_type_name
                
        typeobjs = {t.name : t for t in domain_params[DOMAIN_TYP]}
        def get_type_obj(t):
            if t in typeobjs: 
                ans = typeobjs[t]
                if ans == None:
                    raise ValueError("Cyclic dependency in types")
                return ans
            typeobjs[t] = None
            st_name = types[t]
            supertype = None
            if st_name == None:
                supertype = typeobjs["object"]
            else:
                supertype = get_type_obj(st_name)
            typeobjs[t] = ConstType(t, supertype)
            return typeobjs[t]

        for t, st in types.items():
            if st != None and st not in types:
                raise ValueError(f'Undefined type {st}')
        for t in types.keys():
            domain_params[DOMAIN_TYP].append(get_type_obj(t))
        domain_params[IS_TYPE_SET] = True

    @staticmethod
    def parse_constants(pddl_tree: PddlTree, domain_params):
        const_index = Index()
        if DOMAIN_CONST in domain_params:
            raise ValueError('Redefinition of constants')
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':constants')
        if DOMAIN_REQ in domain_params and domain_params[DOMAIN_REQ].has_typing():
            types = domain_params.get(DOMAIN_TYP, [])
        else:
            types = None
        parse_objects(pddl_iter, const_index, types=types)
        domain_params[DOMAIN_CONST] = const_index.elems
        
    @staticmethod
    def parse_predicates(pddl_tree: PddlTree, domain_params):
        if DOMAIN_PRED in domain_params:
            raise ValueError('Redefinition of predicates')
        pred_index = Index()
        pddl_iter = pddl_tree.iter_elements()
        pddl_iter.assert_token(':predicates')
        while pddl_iter.has_next():
            pred_tokens = pddl_iter.get_group()
            pred_iter = pred_tokens.iter_elements()
            pred_name = pred_iter.get_name()
            if DOMAIN_REQ in domain_params and domain_params[DOMAIN_REQ].has_typing():
                types = domain_params.get(DOMAIN_TYP, [])
            else:
                types = None
            params = parse_parameters(pred_iter, types=types)
            pred = Predicate(pred_name, params)
            if pred_index.find_index(pred) != None:
                raise ValueError(f'Duplicate predicate {pred_name}')
            
            pred.set_id(pred_index.get_index(pred))
        domain_params[DOMAIN_PRED] = pred_index.elems

    @staticmethod
    def parse_action(pddl_tree: PddlTree, domain_params):
        if DOMAIN_ACT not in domain_params:
            domain_params[DOMAIN_ACT] = []
        if DOMAIN_REQ in domain_params and domain_params[DOMAIN_REQ].has_typing():
            types = domain_params.get(DOMAIN_TYP,[])
        else:
            types = None
        domain_params[DOMAIN_ACT].append(
            Action.parse_action(
                pddl_tree, domain_params.get(DOMAIN_PRED, []),
                domain_params.get(DOMAIN_CONST, []), types))