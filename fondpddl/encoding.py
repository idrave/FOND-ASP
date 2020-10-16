from fondpddl import Problem
from fondpddl.algorithm import GraphIterator
from fondpddl.utils import Index

def clingo_problem_encoding(problem: Problem, iterator: GraphIterator, expand_goal=True, log=False):
    state_index = Index()
    action_index = Index()
    clingo_symbols = []
    for state in iterator.iterate(problem, expand_goal=expand_goal):
        state_index.get_index(state)
        for action, children in state.transitions:
            action_index.get_index(action)
            for child in children:
                state_index.get_index(child)
        clingo_symbols += state.encode_clingo(state_index, action_index)
    if log:
        print('States:')
        for i, elem in enumerate(state_index):
            print(f'State {i}: ', elem.string(problem))
        for i, elem in enumerate(action_index):
            print(f'Action {i}: ', elem.string(problem))

    return clingo_symbols        
