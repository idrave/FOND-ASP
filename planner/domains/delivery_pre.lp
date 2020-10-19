state(((h;-h),(d;-d),(t;-t),(p;-p))).
initialState((-h,d,t,p)).

transition((H,d,T,P),move,(H,(d;-d),t,P)) :- H=(h;-h),T=(t;-t),P=(p;-p).
transition((H,D,t,P),home,(H,d,(t;-t),P)) :- H=(h;-h),D=(d;-d),P=(p;-p).
transition((-h,-d,T,P),pick,(h,-d,T,P)) :- T=(t;-t), P=(p;-p).
transition((h,D,t,P),drop,(-h,D,t,P)) :- D=(d;-d),P=(p;-p).
transition((h,D,-t,p),deliver,(-h,d,-t,(p;-p))) :- D=(d;-d).

action(move;home;pick;drop;deliver).

goal((-h,(d;-d),(t;-t),-p)).

con_A(move, 1).
con_B(deliver,1).
con_B(home,1).

con_A(home,2).
con_B(move,2).

con_A(deliver,3).