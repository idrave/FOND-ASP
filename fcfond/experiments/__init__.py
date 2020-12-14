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
    add_pddl_experiment(experiments, 'foot3x2_unfair_01', 'foot3x2_unfair_01', PDDL_DOM_PATHS/'foot3x2_d.pddl',
                        PDDL_DOM_PATHS/'foot3x2_unfair_01.pddl', DEFAULT_OUT/'foot3x2_unfair_01',
                        FairnessNoIndex)
    football = {}
    for i in range(3, 22, 2):
        istr = str(i).zfill(2)
        add_pddl_experiment(football, 'foot%s'%(istr), 'foot%s'%(istr), PDDL_DOM_PATHS/'football'/'footballnx2.pddl',
                        PDDL_DOM_PATHS/'football'/('p%s.pddl'%(istr)), DEFAULT_OUT/'football'/('foot%s'%(istr)),
                        FairnessNoIndex)
    add_experiment_list(football, 'foot', 'foot', list(football.keys()), DEFAULT_OUT/'football'/'all')
    experiments.update(**football)
    add_experiment_list(experiments, 'benchmark_1', 'benchmark_1',
                        ['qnp'] + \
                        list(fcfond.experiments.ltl.get_experiments().keys()) + \
                        ['foot3x2'], DEFAULT_OUT/'benchmark_1')
    
    return experiments

def run_experiments(names, timeout, memout, output=None, log=False, n=1, planner=None,
                    expgoal=False, k=None, threads=1):
    experiments = get_experiments()
    results = []
    for name in names:
        if name in experiments:
            experiment = experiments[name]
        else:
            raise ValueError(f'Wrong experiment name {name}')
        output = output if output != None else experiment[OUTPUT]
        out_path = Path(output)
        if not out_path.is_dir():
            out_path.mkdir(parents=True)

        res = run_experiment(name, experiments, output, timeout, memout, log=log,
                             n=n, planner=planner, expgoal=expgoal,
                             k=k, threads=threads)
        for result in res:
            format_results(result)
        results += res

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

def run_experiment(name, experiments, output, timelimit,
                   memlimit, log=False, n=1, planner=None, expgoal=False,
                   k=None, threads=1):
    print(name)
    if name in experiments:
        experiment = experiments[name]
    else:
        raise ValueError(f'Wrong experiment name {name}')
    if EXPERIMENTS in experiment:
        results = []
        print(experiment[EXPERIMENTS])
        for exp in experiment[EXPERIMENTS]:
            result = run_experiment(exp, experiments,output,timelimit, memlimit,
                                     log=log, planner=planner,
                                     expgoal=expgoal, k=k, threads=threads)
            results.append(result)
        return experiment[CALLBACK](experiment, results)

    planner = planner if planner != None else experiment[PLANNER].FILE
    if experiment[ENCODING] == CLINGO:
        results = solve_clingo(
                    experiment[PROB_NAME], experiment[CLINGO_PROBLEM],
                    planner, output, timelimit, memlimit,
                    k=k, n=n, threads=threads)
    else:
        assert experiment[ENCODING] == PDDL
        results = solve_pddl(
                    experiment[PROB_NAME], experiment[PDDL_DOMAIN],
                    experiment[PDDL_PROBLEM], planner, output,
                    experiment[GRAPH_ITER](), timelimit, memlimit, expand_goal=expgoal or experiment[EXPGOAL],
                    log=log, k=k, n=n, threads=threads)
    
    return [results]

def print_experiments(names):
    experiments = get_experiments()
    for name in names:
        if name in experiments:
            experiment = experiments[name]
        else:
            print(f'Wrong experiment name {name}')
        print(name)
        for key, value in experiment.items():
            print('\t'+str(key), value)