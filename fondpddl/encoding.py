from fondpddl import Problem
from fondpddl.algorithm import GraphIterator
from fondpddl.utils import Index
from fcfond.names import STATE_N, ACTION_N
import clingo

def node_1(node):
    return clingo.Function('node', [node])

def edge_1(node_1, node_2):
    return clingo.Function('edge', [clingo.Function('', [node_1, node_2])])

def tlabel_2(node_1, node_2, label):
    return clingo.Function('tlabel', [clingo.Function('', [node_1, node_2]), label])

def action_1(action):
    return clingo.Function('action', [action])

def id_2(symbol, id):
    return clingo.Function('id', [symbol, id])

def root_1(node):
    return clingo.Function('root', [node])

def clingo_problem_encoding(problem: Problem, iterator: GraphIterator,
                            expand_goal=True, ids=True, log=False,
                            logdict=None):
    state_index = Index()
    action_index = Index()

    for state in iterator.iterate(problem, expand_goal=expand_goal):
        state_index.get_index(state)
        print('state ', len(state_index), end='\r')
        for action, children in state.transitions:
            action_index.get_index(action)
            for child in children:
                state_index.get_index(child)
        for symbol in state.encode_clingo(state_index, action_index):
            yield symbol
        if ids:
            yield state.id_clingo(state_index, problem)

    for action in action_index:
        for symbol in action.encode_clingo(problem, action_index):
            yield symbol
        if ids:
            yield action.id_clingo(action_index)
    
    if logdict != None:
        logdict[STATE_N] = len(state_index)
        logdict[ACTION_N] = len(action_index)

    if log:
        print('States:')
        for i, elem in enumerate(state_index):
            print(f'State {i}: ', elem.string(problem))
        for i, elem in enumerate(action_index):
            print(f'Action {i}: ', str(elem))

    return

def clingo_problem_graph(problem: Problem, iterator: GraphIterator,
                            expand_goal=True, ids=True, log=False,
                            logdict=None):
    state_index = Index()
    action_index = Index()
    first = True

    for state in iterator.iterate(problem, expand_goal=expand_goal):
        st = state_index.get_index(state)
        yield node_1(st)
        if first:
            yield root_1(st)
            first = False
        print('node ', len(state_index), end='\r')
        for action, children in state.transitions:
            assert len(children) == 1 # deterministic domains
            child = state_index.get_index(children[0])
            yield edge_1(st, child)
            yield tlabel_2(st, child, action_index.get_index(action.action.name))
        if ids:
            yield id_2(node_1(state.string(problem)), state_index.get_index(state))
    if ids:
        for action in action_index:
            yield id_2(action_1(action), action_index.get_index(action))

    if log:
        print('States:')
        for i, elem in enumerate(state_index):
            print(f'State {i}: ', elem.string(problem))
        for i, elem in enumerate(action_index):
            print(f'Action {i}: ', str(elem))

    return