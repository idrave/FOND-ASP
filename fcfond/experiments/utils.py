from fcfond.experiments.names import *
from fcfond.planner import FairnessNoIndex
from fondpddl.algorithm import BreadthFirstSearch
from fcfond.names import *
from fcfond.experiments.names import *
import numpy as np

def add_pddl_experiment(experiments, name, key, domain,
                        problem, output, planner, expgoal=True, callback=None):
    experiments[key] = {
        GRAPH_ITER : BreadthFirstSearch,
        PROB_NAME : name,
        ENCODING : PDDL,
        PDDL_DOMAIN : domain,
        PDDL_PROBLEM : problem,
        OUTPUT : output,
        PLANNER : planner,
        EXPGOAL:expgoal,
        CALLBACK: callback
    }

def add_clingo_experiment(experiments, name, key,
                        problem, output, planner, callback=None):
    experiments[key] = {
        PROB_NAME : name,
        ENCODING : CLINGO,
        CLINGO_PROBLEM : problem,
        PDDL_PROBLEM : problem,
        OUTPUT : output,
        PLANNER : planner,
        CALLBACK: callback
    }

def concat_results(experiment, results):
    final = []
    for result in results:
        if isinstance(result, list):
            final += concat_results(experiment, result)
        else:
            final.append(result)
    return final

def avg_results(experiment, results):
    results = concat_results(experiment, results)
    final = {PROBLEM: experiment[PROB_NAME]}
    finished = []
    final[SAT_N] = 0
    final[UNSAT_N] = 0
    final[TIMEOUT_N] = 0
    final[MEMOUT_N] = 0
    for exp in results:
        if exp[RESULT] == True:
            final[SAT_N] += 1
            finished.append(exp)
        elif exp[RESULT] == False:
            final[UNSAT_N] += 1
            finished.append(exp)
        elif exp[RESULT] == TIMEOUT:
            final[TIMEOUT_N] += 1
        elif exp[RESULT] == MEMOUT:
            final[MEMOUT_N] += 1
        else:
            raise ValueError(f'Unexpected result {exp[RESULT]}')

    def avg_key(key, l, round_=0):
        r = round(np.mean([exp[key] for exp in l]), round_)
        if round_ == 0:
            return int(r)
        return r

    final[PREPROCESS] = avg_key(PREPROCESS, results, 2)
    final[MAXMEM] = avg_key(MAXMEM, finished, 2)
    #final[MODELS] = avg_key(MODELS) #TODO
    final[CALLS] = avg_key(CALLS, finished)
    final[TIME] = avg_key(TIME, finished, 2)
    final[SOLVING] = avg_key(SOLVING, finished, 2)
    final[MODEL1st] = avg_key(MODEL1st, finished, 2)
    final[TIMEUNSAT] = avg_key(TIMEUNSAT, finished, 2)
    final[CPUTIME] = avg_key(CPUTIME, finished, 2)
    final[STATE_N] = avg_key(STATE_N, results)
    final[ACTION_N] = avg_key(ACTION_N, results)
    final[STDOUT] = '\n'.join(exp[PROBLEM]+'\n'+exp[STDOUT] for exp in results)
    return [final]

def add_experiment_list(experiments, name, key, exp_list,
                        output, callback=concat_results):
    experiments[key] = {
        PROB_NAME : name,
        EXPERIMENTS: exp_list,
        OUTPUT : output,
        CALLBACK: callback
    }
