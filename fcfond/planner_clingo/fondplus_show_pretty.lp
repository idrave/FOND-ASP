% Like fondplus.lp but shows policy in pretty format for humans

#program solucionar.
#include "fondplus_core.lp".

% predicate for showing
plan(State, Action) :- policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS).

#show plan/2.


#script(python).
import re

def report_model(m):
    print("Reporting on a model.....")
    # From string model rep extract pairs of the form (3, "DS")
    #print(m)
    plan = re.findall('plan\(\"([^ ]+)\",\"([^ ]+)\"\)', str(m))  # extract each (3, "DS")

    print('=======================================')
    print(f'Solution {m.number} - Size: {len(plan)} - Cost: {m.cost} - Optimal? {m.optimality_proven}')
    for x in plan:
        print(x[0], "\n\t===>", x[1])
    print('=======================================', flush=True)
    pass

def main(prg):
    prg.ground([('base', []),('solucionar', [])])
    prg.solve(on_model=report_model)
#end.