% state(S): S is a state
% initialState(S): S is the initial state
% goal(S): S is a goal state
% action(A): A is an action
% transition(S1, A, S2): S2 belongs to F(S1, A) (F being the transition function)
% policy(S, A): the policy applies action A in S
% reach(S): state S is reachable from initial state following the policy
% pathgoal(S): there exists a path from S to a goal state, following the policy
% edge(S1, S2): (S1, S2) is a valid transition from S1, following the policy
% con_A(A, I): action A belongs to set of constraints A_I
% con_B(A, I): action A belongs to set of constraints B_I

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

#program edges.

edge(St1, St2) :-
    transition(St1, Action, St2), policy(St1, Action).

#program edges_external.

#external edge(St1, St2) :
    transition(St1, Action, St2), policy(St1, Action).

#program terminating(i).

%%%% Termination

% connected(S1, S2, i):
%    there exists a path between S1 and S2 after iteration i of the termination algorithm
% terminating(S1, S2, i):
%    edge (S1, S2) removed at iteration i
% continue(i):
%    whether to compute next iteration

% adjacent states are connected
connected(St1, St2, i) :-
    edge(St1, St2), not goal(St1), not terminating(St1, St2, i).

connected(St1, St3, i) :-
    connected(St1, St2, i), edge(St2, St3), not goal(St2),
    not terminating(St2, St3, i), St1 != St2.

% terminating if there is a "self-path" using a constrained A_j action
% AND no action in possible self-paths is in B_j
terminating(St1, St2, i+1) :-
    edge(St1, St2), policy(St1, Act), not terminating(St1, St2, i),
    connected(St2, St1, i), con_A(Act, J),
    not con_B(Act2, J) :
        connected(St1, T1, i), connected(T2, St2, i),
        edge(T1, T2), policy(T1, Act2), not terminating(T1, T2, i).

% terminating edges pass through iterations
terminating(S1, S2, i+1) :- terminating(S1, S2, i).

% if there are new terminating edges, recalculate connectivity
continue(i) :- terminating(S1, S2, i+1), not terminating(S1, S2, i).

% if no edges where removed in last iteration and there are still cycles
% there policy is not terminating
:-  not continue(i),
    connected(S, S, i), state(S).

% not required if clingo is run with '-n 0' option, which shows all models
% this line is only to guarantee the script will receive the models with no continue(i), if any
#maximize {1 : not continue(i)}.

#script(python).
import clingo
def main(prg):
    prg.ground([('base', [])])
    i = 0
    stop = False
    while not stop:
        print(f'Iteration {i}')
        prg.ground([('terminating', [i])])
        with prg.solve(yield_=True) as handle:
            for model in handle:
                if not model.contains(clingo.Function('continue', [i])): # we have not continue(i)
                    print('Solution: '+','.join(map(str, model.symbols(shown=True)))) # print policy
                    stop = True
                    break
            result = handle.get()
            if result.unsatisfiable: # no terminating policy
                print('UNSAT')
                stop = True
        i += 1
#end.