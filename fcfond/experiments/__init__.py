from pathlib import Path
from fondpddl import encode_clingo_problem
from fondpddl.algorithm import BreadthFirstSearch
from fcfond.run import solve_pddl, solve_clingo, format_results
from fcfond.planner import FairnessNoIndex, DualFondQnpPlanner
from fcfond.experiments.utils import add_pddl_experiment
import pandas as pd

from fcfond.experiments.names import *
import fcfond.experiments.qnp
import fcfond.experiments.ltl

def get_experiments():
    experiments = {**fcfond.experiments.qnp.get_experiments(),
                   **fcfond.experiments.ltl.get_experiments()}
    add_pddl_experiment(experiments, 'foot3x2', 'foot3x2', PDDL_DOM_PATHS/'foot3x2_d.pddl',
                        PDDL_DOM_PATHS/'foot3x2_p.pddl', DEFAULT_OUT/'foot3x2')
    return experiments

def get_experiment_lists():
    benchmark_1 = list(fcfond.experiments.qnp.get_experiments().values()) + \
                  list(fcfond.experiments.ltl.get_experiments().values()) + \
                  [get_experiments()['foot3x2']]
    return {**fcfond.experiments.qnp.get_experiment_lists(),
            **fcfond.experiments.ltl.get_experiment_lists(),
            'benchmark_1': {EXPERIMENTS: benchmark_1, OUTPUT: DEFAULT_OUT/'benchmark_1'}}

def run_experiments(name, output=None, log=False, n=1, index=False, expgoal=False, k=None):
    experiments = get_experiments()
    experiment_lists = get_experiment_lists()
    if name in experiments:
        experiment = [experiments[name]]
        output = output if output != None else experiment[0][OUTPUT]
    elif name in experiment_lists:
        experiment = experiment_lists[name][EXPERIMENTS]
        output = output if output != None else experiment_lists[name][OUTPUT]
    else:
        raise ValueError(f'Wrong experiment name {name}')

    output = output if output != None else experiment[OUTPUT]
    if index:
        planner = DualFondQnpPlanner
    else:
        planner = FairnessNoIndex
    out_path = Path(output)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)
    stdouts = []
    df = pd.DataFrame()
    for exp in experiment:
        if exp[ENCODING] == CLINGO:
            stdout, info = solve_clingo(exp[PROB_NAME], exp[CLINGO_PROBLEM], planner(),
                                output, pre_process=True, k=k, n=n) #TODO preprocess can be changed
        else:
            assert exp[ENCODING] == PDDL
            stdout, info = solve_pddl(exp[PROB_NAME], exp[PDDL_DOMAIN], exp[PDDL_PROBLEM],
                                planner(), output, exp[GRAPH_ITER](), expand_goal=expgoal,
                                log=log, k=k, n=n)
        if log:
            print(stdout)
        stdouts.append(stdout)
        format_results(info)
        df = df.append(info, ignore_index=True)
    df.to_csv(str(Path(output)/'metrics.csv'),index=False)
    if log:
        print(df)
    with open(str(Path(output)/'stdout.txt'), 'w') as fp:
        for stdout in stdouts:
            fp.write(stdout)