% SOLVABLE problem
%
%   https://dot-to-ascii.ggerganov.com/?src_hash=b0ae2593
%
%       digraph {
%           0 -> 1 [ label = "c1" ];
%           1 -> 2 [ label = "a1" ];
%           1 -> 1 [ label = "a1" ];
%           2 -> 3 [ label = "c2" ];
%           3 -> 4 [ label = "a2" ];
%           3 -> 10 [ label = "a2" ];
%           4 -> 5 [ label = "b1" ];
%           4 -> 4 [ label = "b1" ];
%           5 -> 1 [ label = "c3" ];
%       }
%
%                  ┌─────┐
%                  │  0  │
%                  └─────┘
%                    │
%                    │ c1
%                    ▼
%             a1   ┌─────┐
%           ┌───── │     │
%           │      │  1  │
%           └────▶ │     │ ◀┐
%                  └─────┘  │
%                    │      │
%                    │ a1   │
%                    ▼      │
%                  ┌─────┐  │
%                  │  2  │  │
%                  └─────┘  │
%                    │      │
%                    │ c2   │
%                    ▼      │
%   ┌────┐  a2     ┌─────┐  │
%   │ 10 │ ◀────── │  3  │  │
%   └────┘         └─────┘  │ c3
%                    │      │
%                    │ a2   │
%                    ▼      │
%             b1   ┌─────┐  │
%           ┌───── │     │  │
%           │      │  4  │  │
%           └────▶ │     │  │
%                  └─────┘  │
%                    │      │
%                    │ b1   │
%                    ▼      │
%                  ┌─────┐  │
%                  │  5  │ ─┘
%                  └─────┘
%
%  C1: a1/b1
%  C2: a2
%  C3: b1/a1
%
%   Policy will get out of the loop in 3 if we state action a3 is fair too
%
%  C3: a3
%
%       ==================================================
%       Solution 1 - Size: 7 - Cost: [] - Optimal? False
%       ==================================================
%       0: 0
%       	 a1
%       1: 2
%       	 c1
%       2: 3
%       	 a3
%       3: 4
%       	 b1
%       4: 5
%       	 c3
%       5: 6
%       	 a2
%       6: 7
%       	 c4
%       ==================================================
%       Answer: 1
%       plan(0,a1) plan(2,c1) plan(3,a3) plan(4,b1) plan(5,c3) plan(6,a2) plan(7,c4)
%       SATISFIABLE
state(0..5;10).
action(a1;a2;b1;c1;c2;c3).

id(state(N), N) :- state(N).
id(action(N), N) :- action(N).

initialState(0).
goal(10).

transition(0,c1,1).
transition(1,a1,(1;2)).
transition(2,c2,3).
transition(3,a2,(4;10)).
transition(4,b1,(4;5)).
transition(5,c3,1).

% C1: a1/b1
con_A(a1,1).
con_B(b1,1).

% C2: a2
con_A(a2,2).

% C4: b1/a1
con_A(b1,3).
con_B(a1,3).

