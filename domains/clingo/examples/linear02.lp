% A linear problem with 2 non-deterministic actions
%
% 1 --a--> 2 --b--> 3 --c/d--> 4
%          ^        |
%          |       c/d
%          |        |
%           --------
%
%  Plan should be
%       plan(1,a) plan(2,b) plan(3,d)
%
%  in the last step, only d is good 
%       action c cannot be used as it is not guaranteed to be fair in the precense of b

state(1;2;3;4).
action(a;b;c;d).

transition(1,a,2).
transition(2,b,3).
transition(3,c,4).
transition(3,c,2).
transition(3,d,4).
transition(3,d,2).

initialState(1).
goal(4).

id(action(a), a).
id(action(b), b).
id(action(c), c).
id(action(d), d).

id(state(1), 1).
id(state(2), 2).
id(state(3), 3).
id(state(4), 4).

%Var 1: n
con_A(c, 1).
con_B(b, 1).

con_A(d, 2).

