from fcfond.experiments.names import *
from fcfond.run import FairnessNoIndex, FairnessPlanner
from fondpddl.algorithm import BreadthFirstSearch

basic_index = {
        PLANNER : FairnessPlanner,
        PARAM_K : 3,
        GRAPH_ITER : BreadthFirstSearch,
        EXP_GOAL : False}

basic_noindex = {
    PLANNER : FairnessNoIndex,
    GRAPH_ITER : BreadthFirstSearch,
    EXP_GOAL : False}

def add_pddl_experiment(experiments, name, key, domain,
                        problem, output, index=True):
    base = basic_index if index else basic_noindex
    experiments[key] = {
        **base,
        PROB_NAME : name,
        ENCODING : PDDL,
        PDDL_DOMAIN : domain,
        PDDL_PROBLEM : problem,
        OUTPUT : output
    }