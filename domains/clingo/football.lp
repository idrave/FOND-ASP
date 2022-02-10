state((L0, R0, A, L, C, R, VL, VR, T)) :-
    L0=(l;-l), R0=(r;-r), A = 1..3, R = (x;1..3), C = (x;1;3), L = (x;1..3), T=(t;-t),
    VL = (vl;-vl), VR = (vr;-vr),
    L = x : C != x;
    R = x : C != x;
    A != C,
    L = x : L0 = -l;
    R = x : R0 = -r.

initialState((l, r, 2, L, x, R, -vl, -vr, t)) :- state((l, r, 2, L, x, R, -vl, -vr, t)).

transition(S1, right, S2) :-
    S1 = (L01, r, A, _, C1, R1, VL, VR1, t),
    S2 = (l, R02, A, C1, R1, R2, VL, VR2, -t),
    state(S1), state(S2),
    A != R1,
    VR2 = vr : VR1 = vr; VR2 = vr : R02 = -r;
    VR2 = -vr : VR1 = -vr, R02 = r;
    R2 = x : R1 != x;
    R2 = x : R02 = -r.

transition(S1, left, S2) :-
    S1 = (l, R01, A, L1, C1, _, VL1, VR, t),
    S2 = (L02, r, A, L2, L1, C1, VL2, VR, -t),
    state(S1), state(S2),
    A != L1,
    VL2 = vl : VL1 = vl; VL2 = vl : L02 = -l;
    VL2 = -vl : VL1 = -vl, L02 = l;
    L2 = x : L1 != x;
    L2 = x : L02 = -l.

transition(S1, up, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, 2, L, x, R, VL, VR, t),
    S2 = (L0, R0, 1, L, x, R, VL, VR, -t).

transition(S1, up, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, 3, L, x, R, VL, VR, t),
    S2 = (L0, R0, (1;2), L, x, R, VL, VR, -t).

transition(S1, up, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, 3, L, 1, R, VL, VR, t),
    S2 = (L0, R0, 2, L, 1, R, VL, VR, -t).

transition(S1, down, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, 2, L, x, R, VL, VR, t),
    S2 = (L0, R0, 3, L, x, R, VL, VR, -t).

transition(S1, down, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, 1, L, x, R, VL, VR, t),
    S2 = (L0, R0, (2;3), L, x, R, VL, VR, -t).

transition(S1, down, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, 1, L, 3, R, VL, VR, t),
    S2 = (L0, R0, 2, L, 3, R, VL, VR, -t).

transition(S1, defend, S2) :-
    state(S1), state(S2),
    S1 = (L0, R0, A, L1, C1, R1, VL, VR, -t),
    S2 = (L0, R0, A, L2, C2, R2, VL, VR, t),
    L2 = x : L1 = x; R2 = x : R1 = x;
    L2 = (L1-1;L1;L1+1) : L1 != x;
    R2 = (R1-1;R1;R1+1) : R1 != x;
    C2 = x : C1 = x;
    C2 = 1 : C1 = 1, A = 2;
    C2 = 3 : C1 = 3, A = 2;
    C2 = 1..2 : C1 = 1..2, A = 3;
    C2 = 2..3 : C1 = 2..3, A = 1.

action(right; left; up; down; defend).
goal(G) :-
    state(G),
    G = (L0, R0, A, L, C, R, vl, vr, T).

con_A(up, 1).
con_A(down, 2).
con_A(right, 3).
con_B(left, 3).
con_A(left,4).
con_B(right,4).