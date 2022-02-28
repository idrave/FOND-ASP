% A SOLVABLE instance, but care needs to be taken when selecting action at 3
%   bc action a is not fair in the precense of action b
%
%   https://dot-to-ascii.ggerganov.com/?src_hash=5871e6d8
%       digraph {
%              1 -> 2 [ label = "c1" ];
%              2 -> 3 [ label = "b1" ];
%       	   3 -> 2 [ label = "a1,a2" ];
%              3 -> 4 [ label = "a1,a2" ];
%          }
%
%   ┌────────┐
%   │   1    │
%   └────────┘
%     │
%     │ c1
%     ▼
%   ┌────────┐
%   │   2    │ ◀┐
%   └────────┘  │
%     │         │
%     │ b1      │ a1,a2
%     ▼         │
%   ┌────────┐  │
%   │   3    │ ─┘
%   └────────┘
%     │
%     │ a1,a2
%     ▼
%   ┌────────┐
%   │   4    │
%   └────────┘
%
%       C1 = a1/b1
%       C2 = a2
%
%       So, there is a solution, but only if a2 is chosen in state 3
%       Action a1 does not behave fair in 3 because of lop on 2 contains action b1!
%
%   $ python -m fcfond.main -clingo domains/clingo/examples/example01.lp -stats -log -out output
%   ==================================================
%   Solution 1 - Size: 3 - Cost: [] - Optimal? False
%   ==================================================
%   0: 1
%   	 c1
%   1: 2
%   	 b
%   2: 3
%   	 c2
%   ==================================================
%   Answer: 1
%   plan(1,c1) plan(2,b) plan(3,c2)
%   SATISFIABLE
%
%
%   If C2 is commented out, then there is no solution as a2 is an unfair action

state(1;2;3;4).
action(a1;a2;b1;c1).

transition(1,c1,2).
transition(2,b1,3).
transition(3,a1,(4;2)).
transition(3,a2,(4;2)).

initialState(1).
goal(4).

%% Give meaning to actions and states
id(action(push(1,2)), a).
id(state("p;q;-r"), 1).

% a1 is fair only if b1 is not executed (not useful due to loop 3 <--> 2)
con_A(a1, 1).
con_B(b1, 1).

% a2 is fair always (yields solution)
% if commmented out, then a2 becomes un fair and no solution possible
con_A(a2, 2).
