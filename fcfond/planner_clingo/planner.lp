% state(S): S is a state
% initialState(S): S is the initial state
% goal(S): S is a goal state
% action(A): A is an action
% transition(S1, A, S2): S2 belongs to F(S1, A) (F being the transition function)
% policy(S, A): the policy applies action A in S
% reach(S): state S is reachable from initial state following the policy
% pathgoal(S): there exists a path from S to a goal state, following the policy
% edge(S1, S2): (S1, S2) is a valid transition from S1, following the policy
#const k=3.
%#show policy/2.
#show.
#show policy(State, Action) : policy(State, Action), reach(State).
#show id(state(S), ID) : id(state(S), ID).

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

%%%% Termination

iterate(0).

edge(St1, St2) :-
    transition(St1, Action, St2), policy(St1, Action).

connected(St1, St2, I) :-
    edge(St1, St2), not terminating(St1, St2, I),
    iterate(I).

connected(St1, St3, I) :-
    connected(St1, St2, I), edge(St2, St3),
    not terminating(St2, St3, I), iterate(I), St1 != St2.


terminating(St1, St2, I+1) :-
    edge(St1, St2), policy(St1, Act), not terminating(St1, St2, I),
    connected(St2, St1, I), con_A(Act, J),
    not con_B(Act2, J) :
        connected(St2, T1, I), connected(T2, St1, I),
        edge(T1, T2), policy(T1, Act2), not terminating(T1, T2, I).

%*
possible alternative
terminating(St1, St2, I+1) :-
    edge(St1, St2), policy(St1, Act), not terminating(St1, St2, I),
    connected(St2, St1, I), con_A(Act, J), not connected_B(St2, St1, I, J).

connected_B(S1, S2, i, J):-
    edge(S2, S1), not terminating(S2, S1, I), policy(S2, Act), con_A(Act, J),
    connected(S1, T1, I), edge(T1, T2), connected(T2, S2, I), policy(T1, A), con_B(A, J),
    not terminating(T1, T2, I).
*%

terminating(S1, S2, I+1) :- terminating(S1, S2, I), iterate(I).

iterate(I) :- terminating(S1, S2, I), not terminating(S1, S2, I-1), I <= k.

:-  iterate(I), not iterate(I+1),
    connected(S, S, I), state(S).