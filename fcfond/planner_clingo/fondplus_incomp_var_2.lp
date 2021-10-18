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

% changes/3: the policy applies an action in S changing the value of variable K to true/false
atom(K) :- val(K,_).
changes(K,S,1) :- policy(S,A), val(K,S),     eff(K,A,0).
changes(K,S,0) :- policy(S,A), not val(K,S), eff(K,A,1).

% terminating_var/1: variable K can only change its value a finite number of times
terminating_var(K) :- X=0..1, atom(K), terminating(S) : changes(K,S,X).

% fairc/1: B_j is empty or all states applying an action in B_j are terminating, thus appearances of 
% actions in A_j are fair.
fairc(J) :- con_A(_,J), {con_B(A,J)}=0.
fairc(J) :- con_B(_,J), terminating(S) : apply_B(S,J).

% fairc/3: all states with value X (true or false) of variable K where an action in B_j is applied
% can only be traversed finitely often
fairc(J,K,1) :- atom(K), con_B(_,J), terminating(S) : apply_B(S,J),     val(K,S). 
fairc(J,K,0) :- atom(K), con_B(_,J), terminating(S) : apply_B(S,J), not val(K,S).

% fair/1: uses above symbols to express that the policy applies action from A_j in state s,
% and there is a terminating state in all paths from s to itself passing through
% a state that applies an action in B_j
fair(S) :- apply_A(S, J), fairc(J).
fair(S) :- apply_A(S,J), terminating_var(K),     val(K,S), fairc(J,K,1).
fair(S) :- apply_A(S,J), terminating_var(K), not val(K,S), fairc(J,K,0).

% def 15: rule 1
terminating(G) :- goal(G).

% def 15: rule 2
terminating(S) :- fair(S), edge(S, T), terminating(T).

% def 15: rule 3
terminating(S) :- edge(S, _), terminating(T): edge(S, T).

% all states should terminate from goal
:-  not terminating(S), reach(S).

#show policy/2.
#show fairc/1.
#show fairc/3.