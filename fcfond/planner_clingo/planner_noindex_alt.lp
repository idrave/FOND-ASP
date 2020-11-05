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
#show policy/2.

{policy(State, Action): action(Action)} = 1 :- state(State), reach(State).

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

connected(S1, S2) :- edge(S1, S2), not terminating(S1, S2).

connected(S1, St3) :- connected(S1, S2), edge(S2, St3), not terminating(S2, St3), S1 != S2.

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

% extra:
% if successor s3 of s1 is terminating and (s1,s3) is fair,
% (s1,s2) is terminating for any successor s2 of s1
terminating(S1, S2) :-
    policy(S1, A), fair(A), edge(S1, S2),
    edge(S1, S3), terminating(S3).

% if a state is not in a cycle, it is terminating
terminating(S) :- state(S), not connected(S).

%*
% Bad code: some non terminating policies returned
cycle(S1) :- connected(S1, S2), edge(S2, S3), not terminating(S2, S3), connected(S3, S1).
terminating(S) :- state(S), not cycle(S).
*%

terminating(S, S) :-
    edge(S, S), policy(S, Act), con_A(Act, J).

% qnp like termination
terminating(S1, S2) :-
    edge(S1, S2), policy(S1, Act), con_A(Act, J),
    terminating(T1, T2):
        connected(S2, T1), connected(T2, S1),
        edge(T1, T2), policy(T1, Act2), con_B(Act2, J).

%*
% Bad code: some non terminating policies returned
terminating(S1, S2) :-
    edge(S1, S2), policy(S1, Act), con_A(Act, J),
    not con_B(Act2, J) :
        connected(S2, T1), connected(T2, S1),
        edge(T1, T2), policy(T1, Act2), not terminating(T1, T2).
*%

:-  connected(S, S), reach(S).
#show terminating/2.
#show terminating/1.
#show cycle/1.