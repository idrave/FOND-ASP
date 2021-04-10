% This is the FOND+ solver for FOND problems with conditional fairness (ICAPS 2021)
%
% The FOND+ problem needs to be specified using the following atoms:
%
% state(S): S is a state
% initialState(S): S is the initial state
% goal(S): S is a goal state
% action(A): A is an action
% transition(S1, A, S2): S2 belongs to F(S1, A) (F being the transition function)
% con_A(A, I): action A belongs to set of constraints A_I
% con_B(A, I): action A belongs to set of constraints B_I
%
% The OUTPUT of the planner, when there is an answer set model, can be extracted via
% atoms policy/2

% policy(S, A): the policy applies action A in S
{policy(State, Action): action(Action)} = 1 :- state(State), reach(State), not goal(State).

% reach/1: state is reachable following the policy
reach(S2) :-
    reach(S1), transition(S1, Action, S2),
    policy(S1, Action), not goal(S1).


reach(St0) :- initialState(St0).

% edge/2: the policy in s1 chooses an action that can take you to s2
edge(S1, S2) :- transition(S1, Action, S2), policy(S1, Action).

% connected/2: there exists a path from s1 to s2 following the policy
connected(S1, S2) :- edge(S1, S2).
connected(S1, S3) :- connected(S1, S2), edge(S2, S3), S1 != S2.

% blocked/2: expresses that:
% i) there is no path from s1 to s2, or
% ii) all paths from s1 to s2 contain a state that has been marked as terminating
blocked(S1, S2) :- not connected(S1, S2), state(S1), state(S2).
blocked(S1, S2) :- connected(S1, S2), terminating(S1).
blocked(S1, S2) :- connected(S1, S2), terminating(S2).
blocked(S1, S2) :-
    connected(S1, S2), not edge(S1, S2): S1 = S2;
    blocked(T, S2) : edge(S1, T), S1 != T.

blocked2(S, T) :- blocked(S, T ; T, S).

% fair/1: uses above symbols to express that the policy applies action from A_j in state s,
% and there is a terminating state in all paths from s to itself passing through
% a state that applies an action in B_j
fair(S) :-
    policy(S, Act), con_A(Act, J),
    blocked2(S, T): policy(T, A2), con_B(A2, J).

% def 15: rule 1
terminating(G) :- goal(G).

% def 15: rule 2
terminating(S) :- fair(S), edge(S, T), terminating(T).

% def 15: rule 3
terminating(S) :- edge(S, _), terminating(T): edge(S, T).

% all states should terminate from goal
:-  not terminating(S), reach(S).