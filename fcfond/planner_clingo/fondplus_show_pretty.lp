% Runs FONDPLUS standard and pretty prints the policy if found
%
% Using Python hooks: https://potassco.org/clingo/python-api/5.5/clingo/
% Can be done better with Clorm: https://clorm.readthedocs.io/en/latest/clorm/

% the base proram is the FONDPLUS core system
#program fondplus.
#include "fondplus_core.lp".

% program to support visualization/pretty printing and id-mapping
#program plan_show.
#include "plan_api.lp".   % predicates to perform Id mapping for states and actions (if any)

#show.
#show plan/2.   % just show the mapped plan


% For debugging....
% #show blocked2/2.
% #show fair/1.
% #show edge/2.
% #show connected/2.
% #show reachable/1.
% #show terminates/1.

#include "fondplus_show_pretty.py".
