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
%#show policy/2.
#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS). %only for display purposes

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

edge(S1, S2) :- transition(S1, Action, S2), policy(S1, Action), reach(S1), not goal(S1).

terminating(G) :- goal(G).

% if action applied is fair, check at least one successor is terminating
terminating(S) :-
    policy(S, A), fair(A),
    edge(S, S2), terminating(S2).

% if action applied is not fair, check all successors are terminating
terminating(S) :-
    policy(S, A), not fair(A),
    terminating(S, S2) : edge(S, S2).

terminating(S1, S2) :- terminating(S2), edge(S1, S2).


% if a state is not in a cycle, it is terminating
%-cycle(S1):- state(S1), terminating(S2, S3) : connected(S1, S2), edge(S2, S3), connected(S3, S1).
%cycle(S) :- not -cycle(S), state(S).
%terminating(S) :- state(S), -cycle(S).



%:-  cycle(S), reach(S).
:- not terminating(S), reach(S).%%%

