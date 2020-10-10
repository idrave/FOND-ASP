state(1). % -H, n > 0
state(2). % -H, n = 0
state(3). % H, n > 0
state(4). % H, n = 0

action(1). % putaway
action(2). % pickabove
action(3). % putabove
action(4). % pickother

initialState(1).
transition(1, 2, 3).
transition(1, 2, 4).
transition(1, 4, 3).

goal(2).
transition(2, 4, 4).

transition(3, 1, 1).
transition(3, 3, 1).

goal(4).
transition(4, 1, 2).
transition(4, 3, 1).

%Var 1: n
con_A(2, 1).
con_B(3, 1).