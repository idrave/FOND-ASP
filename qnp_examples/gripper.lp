action(ds).
action(dt).
action(ps).
action(m).
action(l).

state(1). % T,b>0,c=0,g>0
initialState(1).

transition(1, l, 2).

state(2). % -T,b>0,c=0,g>0
transition(2, ps, 3).
transition(2, ps, 4).
transition(2, ps, 5).
transition(2, ps, 6).
transition(2, m, 1).

state(3).
transition(3, m, 7).
transition(3, ds, 2).
transition(3, ds, 6).

state(4).
transition(4, m, 8).
transition(4, ds, 2).
transition(4, ds, 6).

state(5).
transition(5, m, 9).
transition(5, ds, 2).
transition(5, ds, 6).

state(6).
transition(6, m, 10).
transition(6, ds, 2).
transition(6, ds, 6).

state(7).
transition(7, l, 3).
transition(7, dt, 8).
transition(7, dt, 11).

state(8).
transition(8, l, 4).
transition(8, dt, 8).
transition(8, dt, 11).

state(9).
transition(9, l, 5).
transition(9, dt, 10).
transition(9, dt, 12).

state(10).
transition(10, l, 6).
transition(10, dt, 10).
transition(10, dt, 12).

state(11).
goal(11).

state(12).
transition(12, l, 1).

%var 1 b
con_A(ps, 1).
con_B(ds, 1).

%var 2 c
con_A(ds, 2).
con_A(dt, 2).
con_B(ps, 2).

%var 3 g
con_A(ps, 3).
con_B(ds, 3).
con_B(dt, 3).