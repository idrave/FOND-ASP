% the the name description of states and actions if prescribed, otherwise take the ids
id_map(state(N), S) :- id(state(N), S).
id_map(state(S), S) :- state(S), not id(state(_), S).
id_map(action(N), A) :- id(action(N), A).
id_map(action(A), A) :- action(A), not id(action(_), A).

