from fcfond.experiments.names import *
from fcfond.planner import FairnessNoIndex
from fondpddl.algorithm import BreadthFirstSearch

basic_exp = {
        GRAPH_ITER : BreadthFirstSearch}

def add_pddl_experiment(experiments, name, key, domain,
                        problem, output):
    experiments[key] = {
        **basic_exp,
        PROB_NAME : name,
        ENCODING : PDDL,
        PDDL_DOMAIN : domain,
        PDDL_PROBLEM : problem,
        OUTPUT : output
    }