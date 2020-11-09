from pathlib import Path
from fondpddl import encode_clingo_problem
from fondpddl.algorithm import BreadthFirstSearch
from fcfond.run import solve_pddl, solve_clingo, FairnessPlanner, FairnessNoIndex, format_results
import pandas as pd

from fcfond.experiments.names import *
import fcfond.experiments.qnp

def get_experiments():
    return {**fcfond.experiments.qnp.get_experiments()}

def get_experiment_lists():
    return {**fcfond.experiments.qnp.get_experiment_lists()}

def run_experiments(name, output=None, log=False, n=1):
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
    out_path = Path(output)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)
    stdouts = []
    df = pd.DataFrame()
    for exp in experiment:
        if exp[ENCODING] == CLINGO:
            stdout, info = solve_clingo(exp[PROB_NAME], exp[CLINGO_PROBLEM], exp[PLANNER](),
                                output, pre_process=True, k=exp.get(PARAM_K, None), n=n) #TODO preprocess can be changed
        else:
            assert exp[ENCODING] == PDDL
            stdout, info = solve_pddl(exp[PROB_NAME], exp[PDDL_DOMAIN], exp[PDDL_PROBLEM],
                                exp[PLANNER](), output, exp[GRAPH_ITER](),
                                exp[EXP_GOAL], log=log, k=exp.get(PARAM_K, None), n=n)
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