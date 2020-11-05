state(((e;-e),(x;-x),(d;-d),(n;-n),(m;-m))).
initialState((e,-x,-d,n,m)).

transition((e,X,D,-n,M),pickx,(-e,x,D,-n,M)) :- X=(x;-x),D=(d;-d),M=(m;-m).
transition((e,X,D,n,M),pickabovex,(-e,X,D,(n;-n),M)) :- X=(x;-x),D=(d;-d),M=(m;-m).
transition((e,X,D,N,m),pickabovey,(-e,X,D,N,(m;-m))) :- X=(x;-x),D=(d;-d),N=(n;-n).
transition((-e,-x,D,N,M),putaside,(e,-x,D,N,M)) :- D=(d;-d),N=(n;-n);M=(m;-m).
transition((-e,x,D,N,M),putxaside,(e,-x,D,N,M)) :- D=(d;-d),N=(n;-n);M=(m;-m).
transition((-e,x,D,N,-m),putxony,(e,-x,d,N,m)) :- D=(d;-d),N=(n;-n).

goal(((e;-e),(x;-x),d,(n;-n),(m;-m))).
action(pickabovex;pickx;pickabovey;putaside;putxaside;putxony).

con_A(pickabovex,1).

con_A(pickabovey,2).
con_B(putxony, 2).
%#show transition/3.