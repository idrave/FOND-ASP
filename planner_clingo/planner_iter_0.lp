% state(S): S is a state
% initialState(S): S is the initial state
% goal(S): S is a goal state
% action(A): A is an action
% transition(S1, A, S2): S2 belongs to F(S1, A) (F being the transition function)
% policy(S, A): the policy applies action A in S
% reach(S): state S is reachable from initial state following the policy
% pathgoal(S): there exists a path from S to a goal state, following the policy
% edge(S1, S2): (S1, S2) is a valid transition from S1, following the policy

#show policy/2.

{policy(State, Action): action(Action)} = 1 :- state(State).
reach(St2) :-
    reach(St1), transition(St1, Action, St2),
    policy(St1, Action).

reach(St0) :- initialState(St0).

pathgoal(Goal) :- goal(Goal).

:- reach(State), not pathgoal(State).

pathgoal(State) :-
    state(State), policy(State, Action),
    transition(State, Action, St2), pathgoal(St2).

edge(St1, St2) :-
    transition(St1, Action, St2), policy(St1, Action).

#program terminating(i).

%%%% Termination

% connected(S1, S2, i):
%    there exists a path between S1 and S2 after iteration i of the termination algorithm
% terminating(S1, S2, i):
%    edge (S1, S2) removed at iteration i
% continue(i):
%    whether to compute next iteration

connected(St1, St2, i) :-
    edge(St1, St2), not goal(St1), not terminating(St1, St2, i).

connected(St1, St3, i) :-
    connected(St1, St2, i), edge(St2, St3), not goal(St2),
    not terminating(St2, St3, i), St1 != St2. %possibly add St1 != St2

terminating(St1, St2, i+1) :-
    edge(St1, St2), policy(St1, Act), not terminating(St1, St2, i),
    connected(St2, St1, i), con_A(Act, J),
    not con_B(Act2, J) :
        connected(St1, T1, i), connected(T2, St2, i),
        edge(T1, T2), policy(T1, Act2), not terminating(T1, T2, i).

%*
possible alternative
terminating(St1, St2, i+1) :-
    edge(St1, St2), policy(St1, Act), not terminating(St1, St2, i),
    connected(St2, St1, i), con_A(Act, J), not connected_B(St2, St1, i, J).

connected_B(S1, S2, i, J):-
    edge(S2, S1), not terminating(S2, S1, i), policy(S2, Act), con_A(Act, J),
    connected(S1, T1, i), edge(T1, T2), connected(T2, S2, i), policy(T1, A), con_B(A, J),
    not terminating(T1, T2, i).
*%

terminating(S1, S2, i+1) :- terminating(S1, S2, i).

continue(i) :- terminating(S1, S2, i+1), not terminating(S1, S2, i).

#program finish(i).

% if no edges where removed in last iteration and there are still self-paths
% there is no solution (UNSAT)
:-  not continue(i),
    connected(S, S, i), state(S).

#maximize {1 : not continue(i)}.
% not required if clingo is run with '-n 0' option, which shows all models
% without this line the python script might not get to the model that finishes first the algorithm

#script(python).
import clingo
def main(prg):
    prg.ground([('base', [])])
    i = 0
    stop = False
    while not stop:
        print(f'Iteration {i}')
        prg.ground([('terminating', [i]), ('finish', [i])])
        with prg.solve(yield_=True) as handle:
            
            for model in handle:
                if not model.contains(clingo.Function('continue', [i])):
                    print('Solution: '+','.join(map(str, model.symbols(shown=True))))
                    stop = True
                    break
            result = handle.get()
            assert not result.unknown
            if result.unsatisfiable:
                print('UNSAT')
                stop = True
        i += 1
#end.