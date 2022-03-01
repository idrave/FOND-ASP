% Only a plan/2 predicate is reported which encodes policy/2 result in the model
% but with actions and states translated via the id/2 predicates if any
%
% Evertyhing together, no Python code

#include "fondplus_core.lp".    % load FONDPLUS core planner

% define plan/2 on top of policy/2 and the id translation if any
#include "plan_api.lp".   % predicates to perform Id mapping for states and actions (if any)

#show.
#show plan/2.   % just show the mapped plan

