% UNSOLVABLE problem
%
%   https://dot-to-ascii.ggerganov.com/?src_hash=e44266de
%
%     digraph {
%              0 -> 2 [ label = "a" ];
%              0 -> 1 [ label = "a" ];
%              1 -> 10 [ label = "c" ];
%              1 -> 2 [ label = "c" ];
%              2 -> 0 [ label = "b" ];
%          }
%
%         b
%     ┌──────────┐
%     │          ▼
%   ┌───┐  a   ┌────┐
%   │ 2 │ ◀─── │ 0  │
%   └───┘      └────┘
%     ▲          │
%     │          │ a
%     │          ▼
%     │   c    ┌────┐
%     └─────── │ 1  │
%              └────┘
%                │
%                │ c
%                ▼
%              ┌────┐
%              │ 10 │
%              └────┘
%  C1: a/b
%  C2: c
%
% There should not be a solution because we can loop infinitely between 0 and 2,
% and such infinite trajectory is valid given the fairness assumptions.
% Hence the effect 0 --a--> 1 is not guaranteeed to happen and we may never get to 10
%
% $ python -m fcfond.main -clingo domains/clingo/examples/example03_2.lp -stats -log

state(0..2;10).
action(a;b;c).

id(state(N), N) :- state(N).
id(action(N), N) :- action(N).

initialState(0).
goal(10).

transition(0,a,(1;2)).
transition(1,c,(10;2)).
transition(2,b,0).

% C1: a1/b1
con_A(a,1).
con_B(b,1).

% C2: action c is always fair!
con_A(c,2).
