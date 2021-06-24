% Like fondplus.lp but performs grounding of #show directives separately from policy search.
% Seems to be more efficient sometimes

#show.  % by default, show nothing

#program mostrar.
#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS). 

#program solucionar.
#include "fondplus_core.lp".


#script(python)
def main(prg):
    prg.ground([('base', []),('solucionar', [])])
    prg.solve() # first solving with no show
    prg.ground([('mostrar', [])])
    prg.solve() # next ground the show
#end.