from fondpddl.problem import Problem
from fondpddl.state import State
from fondpddl.algorithm import GraphIterator
from typing import Iterator

class BreadthFirstSearch(GraphIterator):
    def __init__(self):
        pass

    def iterate(self, problem: Problem, expand_goal=True)->Iterator[State]:
        q = list(problem.get_initial_states())
        visited = {state:state for state in q}
        for state in q:
            state.set_init(True)
        
        while len(q) > 0:
            state = q.pop(0)
            state.set_goal(problem.is_goal(state))
            successors = []
            #print('ITER:', state.string(problem))
            if not expand_goal and state.is_goal:
                state.set_expanded()
                state.set_transitions(successors)
                yield state
                continue
            #atoms = state.atoms.copy()
            for action in problem.valid_actions(state):
                children = []
                for new_state in problem.apply_action(state, action):
                    #print('STATE', new_state.string(problem))
                    #child = visited.get(State.open_state(StaticAtomDict(new_atoms)), None)
                    child = visited.get(new_state, None)
                    if child == None:   # new state
                        #child = State.open_state(StaticAtomDict(new_atoms.copy()))
                        child = new_state
                        child.set_init(False)
                        visited[child] = child
                        q.append(child)
                    children.append(child)
                successors.append((action, children))
            state.set_transitions(successors)
            state.set_expanded()
            yield state
                
