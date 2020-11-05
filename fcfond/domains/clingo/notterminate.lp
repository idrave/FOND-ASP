action(inc).
action(dec).

state(1). % A, B>0
transition(1, dec, 2).
transition(1, dec, 3).
initialState(1).

state(2). % -A, B>0
transition(2, inc, 1).

state(3). % -A, B=0
transition(2, inc, 1).
goal(3).

con_A(dec, 1).
con_B(inc, 1).