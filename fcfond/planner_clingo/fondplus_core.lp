% This is the FOND+ solver for FOND problems with conditional fairness (ICAPS 2021)
%
% The FOND+ problem needs to be specified using the following atoms:
%
%   - state(S): S is a state
%   - action(A): A is an action
%   - initialState(S): S is the initial state
%   - goal(S): S is a goal state
%   - transition(S1, A, S2): S2 belongs to F(S1, A) (F being the transition function)
%
% plus the specification of (conditional) fairness:
%
%   - con_A(A, I): action A belongs to set of constraints A_I
%   - con_B(A, I): action A belongs to set of constraints B_I
%
%   If no con_A(A, _) for an action A, then the action A is unfair/adversarial
%   If con_A(A, _) but no con_B(A,_) for an action A, then A is always fair (as in strong-cyclic)
%
% The OUTPUT of the planner, when there is an answer set, can be extracted via atoms policy/2

% policy(S, A): the policy applies action A in S.
%   Generate exactly one action per state
{policy(S, A): action(A), transition(S, A, _)} = 1 :- state(S), reachable(S), not goal(S).

% reach/1: state is reachable following the policy
reachable(S) :- initialState(S).
reachable(S) :- reachable(S1), not goal(S1), edge(S1, S).

% edge/2: state S2 is a possible successor of S1 via the policy
edge(S1, S2) :- policy(S1, A), transition(S1, A, S2).

% connected/2: there exists a path from s1 to s2 following the policy
connected(S1, S2) :- edge(S1, S2).
connected(S1, S3) :- connected(S1, S2), edge(S2, S3), S1 != S2.

% blocked/2: All paths between S1 and S2 are blocked; or all paths from S2 and S1 are blocked
blocked(S1, S2) :- blocked2(S1, S2).
blocked(S1, S2) :- blocked2(S2, S1).

% blocked2/2: expresses that all paths from S1 to S2 are blocked in that:
% i) there is no path from S1 to S2; or
% ii) all paths from S1 to S2 contain a state that has been marked as terminating
blocked2(S1, S2) :- state(S1), state(S2), not connected(S1, S2).
blocked2(S1, S2) :- connected(S1, S2), terminates(S1).
blocked2(S1, S2) :- connected(S1, S2), terminates(S2).

% blocked2(S1, S2) :-     % OPTION 1
%     connected(S1, S2), not edge(S1, S2): S1 = S2 ;
%     blocked2(T, S2) : edge(S1, T), S1 != T.

blocked2(S1, S2) :-   % OPTION 2: as in the paper
    connected(S1, S2), blocked2(T, S2) : edge(S1, T), connected(T, S2).


% fair/1: uses above symbols to express that the policy applies action from A_i in state s,
%   and there is a terminating state in all paths from s to itself passing through
%   a state that applies an action in B_i
%   Works well with OPTION 1 above for blocked2/2
% fair(S) :- policy(S, A), con_A(A, I), blocked(S, T): policy(T, B), con_B(B, I).

% As in paper:;  should work together with OPTION 2 above for blocked/2
%   Seems to yield TWO models, but model 2 is a super set of model 1?
fair(S) :- policy(S, A), con_A(A, I), blocked2(T, S): policy(T, B), con_B(B, I), not blocked2(S, T).

% Interesting this would not work!
% fair(S) :- policy(S, A), con_A(A, I), blocked(S, T): policy(T, B), con_B(B, I).

% terminate/1: a state terminates, i.e., will not be visited forever; as per Def 15
terminates(S) :- goal(S).                               % def 15: rule 1
terminates(S) :- fair(S), edge(S, T), terminates(T).    % def 15: rule 2
terminates(S) :- edge(S, _), terminates(T): edge(S, T). % def 15: rule 3

% all states reachable should terminate (eventually evolve to the goal)
:-  reachable(S), not terminates(S).

% Dummy entries to avoid warning if domain has no con_A/2 or con_B/2
%   if deleted, then warning will be issued by clingo (not serious)
con_A(dummy,-1).
con_B(dummy,-1).