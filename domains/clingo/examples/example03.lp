% SOLVABLE problem
%
%   https://dot-to-ascii.ggerganov.com/?src_hash=73fe8887
%
%     digraph {
%              0 -> 0 [ label = "a" ];
%              0 -> 1 [ label = "a" ];
%              1 -> 10 [ label = "c" ];
%              1 -> 2 [ label = "c" ];
%              2 -> 0 [ label = "b" ];
%          }
%
%              ┌────┐   a
%              │    │ ────┐
%         b    │ 0  │     │
%     ┌──────▶ │    │ ◀───┘
%     │        └────┘
%     │          │
%     │          │ a
%     │          ▼
%   ┌───┐  c   ┌────┐
%   │ 2 │ ◀─── │ 1  │
%   └───┘      └────┘
%                │
%                │ c
%                ▼
%              ┌────┐
%              │ 10 │
%              └────┘
%  C1: a/b
%  C2: c
%
% There should be a solution because it can exit at 1 to the goal since c is always fair
% Action a at 0 will also behave fair despite b because the loop contains an exit at 1


state(0..2;10).
action(a;b;c).

id(state(N), N) :- state(N).
id(action(N), N) :- action(N).

initialState(0).
goal(10).

transition(0,a,(0;1)).
transition(1,c,(10;2)).
transition(2,b,0).

% C1: a1/b1
con_A(a,1).
con_B(b,1).

% C2: action c is always fair!
con_A(c,2).


