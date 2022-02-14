% A loop unsolvable problem problem with 2 non-deterministic actions
%
%                    a3
%                    ||
%                    |v
% 0 --a1--> 2 --c1--> 3 --a2--> 4 --b1--> 5 --c3--> 6 --a2--> 7 --c4--> 0
% |                                                 |
% v                                                 |
% 1  <------------------a2---------------------------
%
%  C1: a1/b1
%  C2: a2
%
% This is an optional conditional fairness:
%
%  C3: a3
%
%  If C3 is there, then there is a solution; otherwise there is none
%   as policy can get trapped at state 3
%

state(0;1;2;3;4;5;6;7).
action(a1;a2;a3;b1;c1;c2;c3;c4;c5).

initialState(0).
goal(1).

transition(0,a1,(1;2)).
transition(2,c1,3).
transition(3,a3,(3;4)).
transition(4,b1,5).
transition(5,c3,6).
transition(6,a2,(1;7)).
transition(7,c4,0).

% First conditional C1: a1/b1
con_A(a1,1).
con_B(b1,1).

% Second conditional C2: a2
con_A(a2,2).

% Third conditional C3: a2/
% if commented out, then NO solution as system can get trapped at 3
con_A(a3,3).
