% This version solves the problem first, and THEN grounds plan/2 separately on top of policy/2 and id/2
% It seems to run faster in some cases

#program solucionar.
#include "fondplus_core.lp".

#program mostrar.
#include "plan_api.lp".   % predicates to perform Id mapping for states and actions (if any)


% This is for the whole program above (both solucionar and mostrar together): just show plan/2
#show.  % by default, show nothing
#show plan/2.

#script(python)
def main(prg):
    # the base program will contain the problem spec; solucionar is FOND+ code
    prg.ground([('base', []), ('solucionar', [])])
    prg.solve() # first solving with no show

    # next, once problem has been solved, ground the showing part of the program
    prg.ground([('mostrar', [])])
    prg.solve() # next ground the show
#end.