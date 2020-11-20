from fcfond.experiments.names import *
from fcfond.planner import FairnessNoIndex
from fondpddl.algorithm import BreadthFirstSearch
from fcfond.names import *
from fcfond.experiments.names import *

def add_pddl_experiment(experiments, name, key, domain,
                        problem, output, planner, callback=None):
    experiments[key] = {
        GRAPH_ITER : BreadthFirstSearch,
        PROB_NAME : name,
        ENCODING : PDDL,
        PDDL_DOMAIN : domain,
        PDDL_PROBLEM : problem,
        OUTPUT : output,
        PLANNER : planner,
        CALLBACK: callback
    }

def avg_results(experiment, results):
    results = concat_results(experiment, results)
    final = {PROBLEM: experiment[PROB_NAME]}
    final[PREPROCESS] = round(sum(exp[PREPROCESS] for exp in results)/len(results), 3)
    final[MAXMEM] = round(sum(exp[PREPROCESS] for exp in results)/len(results), 2)
    final[SAT] = round(100*sum(exp[SAT] for exp in results)/len(results), 2)
    final[MODELS] = int(sum(exp[MODELS] for exp in results)/len(results))
    final[CALLS] = int(sum(exp[CALLS] for exp in results)/len(results))
    final[TIME] = round(sum(exp[PREPROCESS] for exp in results)/len(results), 2)
    final[SOLVING] = round(sum(exp[SOLVING] for exp in results)/len(results), 2)
    final[MODEL1st] = round(sum(exp[MODEL1st] for exp in results)/len(results), 2)
    final[TIMEUNSAT] = round(sum(exp[TIMEUNSAT] for exp in results)/len(results), 2)
    final[CPUTIME] = round(sum(exp[CPUTIME] for exp in results)/len(results), 2)
    final[STATE_N] = int(sum(exp[STATE_N] for exp in results)/len(results))
    final[ACTION_N] = int(sum(exp[ACTION_N] for exp in results)/len(results))
    final[STDOUT] = '\n'.join(exp[PROB_NAME]+'\n'+exp[STDOUT] for exp in results)
    return final

def concat_results(experiment, results):
    final = []
    for result in results:
        if isinstance(result, list):
            final += concat_results(experiment, results)
        else:
            final.append(result)
    return final

def add_experiment_list(experiments, name, key, exp_list,
                        output, callback=concat_results):
    experiments[key] = {
        PROB_NAME : name,
        EXPERIMENTS: exp_list,
        OUTPUT : output,
        CALLBACK: callback
    }
