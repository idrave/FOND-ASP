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
#const k=3.
#show.
%#show policy(State, Action) : policy(State, Action), reach(State).
#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS).

{policy(State, Action): action(Action)} = 1 :- state(State), reach(State), not goal(State).

reach(S2) :-
    reach(S1), transition(S1, Action, S2),
    policy(S1, Action), not goal(S1).

reach(St0) :- initialState(St0).

pathgoal(Goal) :- goal(Goal).

:- reach(State), not pathgoal(State).

pathgoal(State) :-
    state(State), policy(State, Action), reach(State),
    transition(State, Action, S2), pathgoal(S2).

%%%% Termination

iterate(0).

edge(S1, S2) :-
    transition(S1, Action, S2), policy(S1, Action), reach(S1), not goal(S1).

connected(S1, S2, I) :-
    edge(S1, S2), not terminating(S1, S2, I),
    iterate(I), I = 0..k.

connected(S1, St3, I) :-
    connected(S1, S2, I), edge(S2, St3),
    not terminating(S2, St3, I), iterate(I), S1 != S2.

%%%%%%%%%%% new rules %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
terminating(G, 0) :- goal(G).

% if action applied is fair, check at least one successor is terminating
terminating(S, I) :-
    policy(S, A), fair(A), iterate(I),
    edge(S, S2), terminating(S2, I).

terminating(S, I) :-
    policy(S, A), not fair(A), iterate(I),
    terminating(S, S2, I) : edge(S, S2).

terminating(S1, S2, I) :- terminating(S2, I), edge(S1, S2).
terminating(S, I) :- terminating(S, I-1), iterate(I).

% extra:
terminating(S, I+1) :- state(S), not connected(S, S, I), iterate(I).
%terminating(S, I) :- state(S), not connected(S, S, I), iterate(I).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

terminating(S1, S2, I+1) :-
    edge(S1, S2), policy(S1, Act), not terminating(S1, S2, I),
    connected(S2, S1, I), con_A(Act, J), iterate(I),
    not con_B(Act2, J) :
        connected(S2, T1, I), connected(T2, S1, I),
        edge(T1, T2), policy(T1, Act2), not terminating(T1, T2, I).

terminating(S1, S2, I+1) :- terminating(S1, S2, I), iterate(I), I = 0..k.

iterate(I) :- terminating(S1, S2, I), not terminating(S1, S2, I-1), I = 0..k.

:-  iterate(I), not iterate(I+1),
    connected(S, S, I), state(S), I = 0..k.