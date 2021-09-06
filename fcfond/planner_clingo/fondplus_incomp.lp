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

% fairc/1: all states applying an action in B_x are terminating, thus appearances of 
% actions in A_x are fair.
fairc(X) :- con_B(_,X), terminating(S) : policy(S, A), con_B(A, X). 

% fair/1: uses above symbols to express that the policy applies action from A_j in state s,
% where occurrences of actions in A_j are fair.
fair(S) :- policy(S, Act), con_A(Act, J), fairc(J).

% def 15: rule 1
terminating(G) :- goal(G).

% def 15: rule 2
terminating(S) :- fair(S), edge(S, T), terminating(T).

% def 15: rule 3
terminating(S) :- edge(S, _), terminating(T): edge(S, T).

% all states should terminate from goal
:-  not terminating(S), reach(S).