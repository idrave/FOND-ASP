from fondpddl import Problem
from fondpddl.algorithm import GraphIterator
from fondpddl.utils import Index
from fcfond.names import STATE_N, ACTION_N

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
