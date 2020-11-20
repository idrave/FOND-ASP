from pathlib import Path
from fondpddl import encode_clingo_problem
from fondpddl.algorithm import BreadthFirstSearch
from fcfond.run import solve_pddl, solve_clingo, format_results
from fcfond.planner import FairnessNoIndex, DualFondQnpPlanner
from fcfond.experiments.utils import add_pddl_experiment, add_experiment_list
import pandas as pd

from fcfond.experiments.names import *
from fcfond.names import STDOUT, PROBLEM
import fcfond.experiments.qnp
import fcfond.experiments.ltl
import fcfond.experiments.fondsat
from fcfond.planner import FairnessNoIndex

def get_experiments():
    experiments = {**fcfond.experiments.qnp.get_experiments(),
                   **fcfond.experiments.ltl.get_experiments(),
                   **fcfond.experiments.fondsat.get_experiments()}
    add_pddl_experiment(experiments, 'foot3x2', 'foot3x2', PDDL_DOM_PATHS/'foot3x2_d.pddl',
                        PDDL_DOM_PATHS/'foot3x2_p.pddl', DEFAULT_OUT/'foot3x2',
                        FairnessNoIndex)
    add_pddl_experiment(experiments, 'football_5', 'football_5', PDDL_DOM_PATHS/'football'/'footballnx2.pddl',
                        PDDL_DOM_PATHS/'football'/'football_5.pddl', DEFAULT_OUT/'football_5',
                        FairnessNoIndex)
    add_pddl_experiment(experiments, 'football_3', 'football_3', PDDL_DOM_PATHS/'football'/'footballnx2.pddl',
                        PDDL_DOM_PATHS/'football'/'football_3.pddl', DEFAULT_OUT/'football_3',
                        FairnessNoIndex)
    add_pddl_experiment(experiments, 'football_6', 'football_6', PDDL_DOM_PATHS/'football'/'footballnx2.pddl',
                        PDDL_DOM_PATHS/'football'/'football_6.pddl', DEFAULT_OUT/'football_6',
                        FairnessNoIndex)

    add_experiment_list(experiments, 'benchmark_1', 'benchmark_1',
                        list(fcfond.experiments.qnp.get_experiments().values()) + \
                        list(fcfond.experiments.ltl.get_experiments().values()) + \
                        [experiments['foot3x2']], DEFAULT_OUT/'benchmark_1')
    
    return experiments

def run_experiments(name, output=None, log=False, n=1, planner=None, expgoal=False, k=None):
    experiments = get_experiments()
    if name in experiments:
        experiment = experiments[name]
    else:
        raise ValueError(f'Wrong experiment name {name}')
    
    output = output if output != None else experiment[OUTPUT]
    out_path = Path(output)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)

    results = run_experiment(experiment, output, log=log, n=n, planner=planner, expgoal=expgoal, k=k)
    for result in results:
        format_results(result)

    stdout = ''
    for result in results:
        stdout += result[PROBLEM]+'\n'
        stdout += result[STDOUT]+'\n'
    if log:
        print(stdout)
    df = pd.DataFrame(results).drop(STDOUT, axis=1)
    df.to_csv(str(Path(output)/'metrics.csv'),index=False)

    if log:
        print(df)
    with open(str(Path(output)/'stdout.txt'), 'w') as fp:
        fp.write(stdout)

def run_experiment(experiment, output, log=False, n=1, planner=None, expgoal=False, k=None):
    if EXPERIMENTS in experiment:
        results = []
        for exp in experiment[EXPERIMENTS]:
            result = run_experiment(exp, output=output, log=log, planner=planner,
                                     expgoal=expgoal, k=k)
            results.append(result)
        return experiment[CALLBACK](experiment, results)

    planner = planner if planner != None else experiment[PLANNER]
    if experiment[ENCODING] == CLINGO:
        results = solve_clingo(
                    experiment[PROB_NAME], experiment[CLINGO_PROBLEM],
                    planner(), output, pre_process=True, k=k, n=n) #TODO preprocess can be changed
    else:
        assert experiment[ENCODING] == PDDL
        results = solve_pddl(
                    experiment[PROB_NAME], experiment[PDDL_DOMAIN],
                    experiment[PDDL_PROBLEM], planner(), output,
                    experiment[GRAPH_ITER](), expand_goal=expgoal,
                    log=log, k=k, n=n)
    
    return [results]