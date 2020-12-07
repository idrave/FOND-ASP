% state(S): S is a state
% initialState(S): S is the initial state
% goal(S): S is a goal state
% action(A): A is an action
% transition(S1, A, S2): S2 belongs to F(S1, A) (F being the transition function)
% policy(S, A): the policy applies action A in S
% reach(S): state S is reachable from initial state following the policy
% pathgoal(S): there exists a path from S to a goal state, following the policy
% edge(S1, S2): (S1, S2) is a valid transition from S1, following the policy
% fair(A):     action A has strong cyclic fairness 
% con_A(A, I): action A belongs to set of constraints A_I
% con_B(A, I): action A belongs to set of constraints B_I


#show.
#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS). %only for display purposes

{policy(State, Action): action(Action)} = 1 :- state(State), reach(State), not goal(State).

reach(S2) :-
    reach(S1), transition(S1, Action, S2),
    policy(S1, Action), not goal(S1).

reach(St0) :- initialState(St0).

%%%% Termination

edge(S1, S2) :- transition(S1, Action, S2), policy(S1, Action), reach(S1), not goal(S1).

connected(S1, S2) :- edge(S1, S2).
connected(S1, St3) :- connected(S1, S2), edge(S2, St3), S1 != S2.


% check whether all paths from S1 to S2 have terminating edges
nopath(S1, S2) :-
    connected(S1, S2),
    nopath(T, S2) : edge(S1, T), connected(T, S2).

nopath(S1, S2) :- connected(S1, S2), terminating(S1).
nopath(S1, S2) :- connected(S1, S2), terminating(S2).
nopath(S1, S2) :- reach(S1), reach(S2), not connected(S1, S2).

terminating(G) :- goal(G).

terminating(S) :- reach(S), edge(S, T), terminating(T), nopath(S, S).

% qnp like termination

terminating(S) :-
    policy(S, Act), con_A(Act, J), edge(S, T), terminating(T),
    nopath_con(S, U, J): differ(S, U, J).

% mark pairs of edges that decrease/decrease a variable respectively
differ(S, T, J) :-
    policy(S, A1), con_A(A1, J),
    policy(T, A2), con_B(A2, J).

nopath_con(S, T, J) :- differ(S, T, J), nopath(S, T).
nopath_con(S, T, J) :- differ(S, T, J), nopath(T, S).

:-  not terminating(S), reach(S).
