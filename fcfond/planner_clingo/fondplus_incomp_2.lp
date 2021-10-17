% This is a sound, but incomplete FOND+ solver for FOND problems with conditional fairness (ICAPS 2021)
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

% apply_A/2: policy applies action in set A_j in state S (resp. for apply_B/2 and B_j)
apply_A(S,J) :- policy(S,A), con_A(A,J).
apply_B(S,J) :- policy(S,A), con_B(A,J).

% fairc/1: B_j is empty or all states applying an action in B_j are terminating, thus appearances of 
% actions in A_j are fair.
fairc(J) :- con_A(_,J), {con_B(A,J)}=0.
fairc(J) :- con_B(_,J), terminating(S) : apply_B(S,J). 

% fair/1: uses above symbols to express that the policy applies action from A_j in state s,
% and there is a terminating state in all paths from s to itself passing through
% a state that applies an action in B_j
fair(S) :- apply_A(S, J), fairc(J).

% def 15: rule 1
terminating(G) :- goal(G).

% def 15: rule 2
terminating(S) :- fair(S), edge(S, T), terminating(T).

% def 15: rule 3
%terminating(S) :- edge(S, _), terminating(T): edge(S, T).

% additional rule for self-loops
%terminating(S) :- edge(S, U), S != U, apply_A(S,_), terminating(T): edge(S, T), T != S.

% Involves both commented above in one rule:
suc_diff(S) :- edge(S, U), S != U.
terminating(S) :- suc_diff(S), terminating(T): edge(S, T), T != S; apply_A(S, _) : edge(S, S).

% all states should terminate from goal
:-  not terminating(S), reach(S).