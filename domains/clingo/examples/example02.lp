% A UNSAT problem problem with 3 non-deterministic a1, a2, a3
%
%   https://dot-to-ascii.ggerganov.com/?src_hash=73fe8887
%
%       digraph {
%           0 -> 1 [ label = "A1" ];
%           0 -> 2 [ label = "A1" ];
%           2 -> 3 [ label = "c1" ];
%           3 -> 3 [ label = "a3" ];
%           3 -> 4 [ label = "a3" ];
%           4 -> 5 [ label = "B1" ];
%
%           5 -> 6 [ label = "c3" ];
%           6 -> 7 [ label = "A2" ];
%           6 -> 1 [ label = "a2" ];
%           7 -> 0 [ label = "c4" ];
%       }
%
%
%
%             c4      +-----+
%         +---------> |  0  | -+
%         |           +-----+  |
%         |             |      |
%         |             | A1   |
%         |             v      |
%         |           +-----+  |
%         |           |  2  |  |
%         |           +-----+  |
%         |             |      |
%         |             | c1   |
%         |             v      |
%         |      a3   +-----+  |
%         |    +----- |     |  |
%         |    |      |  3  |  |
%         |    +----> |     |  |
%         |           +-----+  |
%         |             |      |
%         |             | a3   |
%         |             v      |
%         |           +-----+  | A1
%         |           |  4  |  |
%         |           +-----+  |
%         |             |      |
%         |             | B1   |
%         |             v      |
%         |           +-----+  |
%         |           |  5  |  |
%         |           +-----+  |
%         |             |      |
%         |             | c3   |
%         |             v      |
%       +---+  A2     +-----+  |
%       | 7 | <------ |  6  |  |
%       +---+         +-----+  |
%                       |      |
%                       | a2   |
%                       v      |
%                     +-----+  |
%                     |  1  | <+
%                     +-----+
%
%  C1: a1/b1
%  C2: a2
%
%   Policy can be stuck at 3 -a3-> 3 bc a3 is NOT fair
%
%       $ python -m fcfond.main -clingo domains/clingo/examples/loop02.lp -stats -log -out output.linear
%       Solving...
%       UNSATISFIABLE
%
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

% Third conditional C3: a2
% if uncommented, then a solution will be found as loop in 3 is fair
con_A(a3,3).
