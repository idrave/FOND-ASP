% Like fondplus.lp but shows policy in pretty format for humans
%
% Using Python hooks: https://potassco.org/clingo/python-api/5.5/clingo/
% Can be done better with Clorm: https://clorm.readthedocs.io/en/latest/clorm/

% the base proram is the FONDPLUS core system
#include "fondplus_core.lp".

% program to support visualization/pretty printing
#program visualize.
% predicate for showing
plan(S, A) :- id2(state(S), IdS), id2(action(A), IdA), policy(IdS, IdA), reachable(IdS).

% the the name description of states and actions if prescribed, otherwise take the ids
id2(state(N), S) :- id(state(N), S).
id2(state(S), S) :- state(S), not id(state(_), S).
id2(action(N), A) :- id(action(N), A).
id2(action(A), A) :- action(A), not id(action(_), A).

#show plan/2.


#script(python)
import re

def report_model(m):
    """
        Report model m

        @arg m : clingo.solving.Model (https://potassco.org/clingo/python-api/5.5/clingo/solving.html#clingo.solving.Model)
    """
    # print("type of model: ", type(m))
    # print("Model: ", m)
    # print(m.symbols(shown=True))

    # old way where we parsed the str rep of the model, not anymore, we use it as object!
    #plan = re.findall('plan\(state\((.+?)\),action\((.+?)\)\)', str(m))  # extract each (3, "DS")

    # extract set of rules from the plan/2 in the model returned as a clingo.solving.Model
    plan = []
    for f in m.symbols(shown=True): # extract function plan(State, Action)
        state = f.arguments[0]
        action = f.arguments[1]
        plan.append((state, action))

    print('='*50)
    print(f'Solution {m.number} - Size: {len(plan)} - Cost: {m.cost} - Optimal? {m.optimality_proven}')
    #print(str(m))
    print('='*50)


    for i, rule in enumerate(plan):
        print(f"{i}: {rule[0]}\n\t {rule[1]}")
    print('='*50, flush=True)
    pass

def main(prg):
    # combine the base program (FOND-ASP) with
    # the small visualize above to show the policy found ground both
    prg.ground([('base', []), ('visualize', [])])

    # solve it and call report_model(m) when a model is found
    prg.solve(on_model=report_model)
#end.