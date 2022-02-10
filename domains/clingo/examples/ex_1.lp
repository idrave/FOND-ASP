state(s1;s2;s3;goal). % s, s', s'', goal
action(a;b;c).
initialState(s1).
goal(goal).

transition(s1, a, (s1;s2)).
transition(s2, b, (s3;goal)).
transition(s3, c, s1).

fair(a).
con_A(b, 1).