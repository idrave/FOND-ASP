from pathlib import Path
from fondpddl import encode_clingo_problem
from fondpddl.algorithm import BreadthFirstSearch
from fcfond.run import solve_pddl, solve_clingo, format_results
import fcfond
from fcfond.experiments.utils import add_pddl_experiment, add_experiment_list
import pandas as pd

from fcfond.experiments.names import *
from fcfond.names import STDOUT, PROBLEM
import fcfond.experiments.qnp
import fcfond.experiments.ltl
import fcfond.experiments.fondsat
import fcfond.experiments.synthetic

def list_experiments(name):
    experiments = get_experiments()
    if not len(name):
        print('Experiments lists:')
        print('\tqnp\n\tltl\n\tfond_sat\n\tnested\n\tsequential\n\tunfair_qnp\n\tfoot\n\tfoot_cyclic\n\tbenchmark_1')
        return
    
    if name not in experiments or EXPERIMENTS not in experiments[name]:
        raise ValueError('Input %s is not a valid list of experiments' % (name))

    lists = []
    exps = []
    for e in experiments[name][EXPERIMENTS]:
        if EXPERIMENTS in experiments[e]:
            lists.append(e)
        else:
            exps.append(e) 

    print('Listing %s:' % (name))
    if len(lists):
        print('Experiments lists:')
        for exp in lists:
            print('\t'+exp)
    if len(exps):
        print('Single experiments:')
        for exp in exps:
            print('\t'+exp)

def get_experiments():
    experiments = {**fcfond.experiments.qnp.get_experiments(),
                   **fcfond.experiments.ltl.get_experiments(),
                   **fcfond.experiments.fondsat.get_experiments(),
                   **fcfond.experiments.synthetic.get_experiments()}
    add_pddl_experiment(experiments, 'foot3x2', 'foot3x2', PDDL_DOM_PATHS/'foot3x2_d.pddl',
                        PDDL_DOM_PATHS/'foot3x2_p.pddl', DEFAULT_OUT/'foot3x2',
                        fcfond.planner.FONDPLUS)
    add_pddl_experiment(experiments, 'foot3x2_unfair_01', 'foot3x2_unfair_01', PDDL_DOM_PATHS/'foot3x2_d.pddl',
                        PDDL_DOM_PATHS/'foot3x2_unfair_01.pddl', DEFAULT_OUT/'foot3x2_unfair_01',
                        fcfond.planner.FONDPLUS)
    football = {}
    football_sc = {}
    for i in range(3, 22, 2):
        istr = str(i).zfill(2)
        add_pddl_experiment(football, 'foot%s'%(istr), 'foot%s'%(istr), PDDL_DOM_PATHS/'football'/'footballnx2.pddl',
                        PDDL_DOM_PATHS/'football'/('p%s.pddl'%(istr)), DEFAULT_OUT/'football'/('foot%s'%(istr)),
                        fcfond.planner.FONDPLUS)
    for i in range(5, 81, 5):
        istr = str(i).zfill(2)
        add_pddl_experiment(football_sc, 'foot%s_cyclic'%(istr), 'foot%s_cyclic'%(istr), PDDL_DOM_PATHS/'football'/'footballnx2.pddl',
                        PDDL_DOM_PATHS/'football'/('p%s.pddl'%(istr)), DEFAULT_OUT/'football'/('foot%s_cyclic'%(istr)),
                        fcfond.planner.STRONGCYCLIC)
    add_experiment_list(football, 'foot', 'foot', list(football.keys()), DEFAULT_OUT/'football'/'all')
    add_experiment_list(football_sc, 'foot_cyclic', 'foot_cyclic', list(football_sc.keys()), DEFAULT_OUT/'football'/'all_cyclic')
    experiments.update(**football)
    experiments.update(**football_sc)
    add_experiment_list(experiments, 'benchmark_1', 'benchmark_1',
                        ['qnp'] + \
                        list(fcfond.experiments.ltl.get_experiments().keys()) + \
                        ['foot3x2'], DEFAULT_OUT/'benchmark_1')
    
    return experiments

def run_experiments(names, timeout, memout, output=None, n=1, planner=None,
                    expgoal=False, k=None, threads=1, stats=True, atoms=False, track=False):
    experiments = get_experiments()
    results = []
    for name in names:
        if name in experiments:
            experiment = experiments[name]
        else:
            raise ValueError(f'Wrong experiment name {name}')
        out = output if output != None else experiment[OUTPUT]
        out_path = Path(out)
        if not out_path.is_dir():
            out_path.mkdir(parents=True)

        res = run_experiment(name, experiments, out, timeout, memout,
                             n=n, planner=planner, expgoal=expgoal,
                             k=k, threads=threads, atoms=atoms, track=track)
        for result in res:
            format_results(result)
        results += res

    stdout = ''
    for result in results:
        stdout += result[PROBLEM]+'\n'
        stdout += result[STDOUT]+'\n'
    fcfond.logger.debug(stdout)
    df = pd.DataFrame(results).drop(STDOUT, axis=1)
    out_path = Path(output if output != None else OUTPUT)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)
    df.to_csv(str(out_path/'metrics.csv'),index=False)

    if stats:
        for col in df.columns:
            print(f"{col}: {df.iloc[0][col]}") # TODO does not work well for multiple experiments
        print()
        print(df)
    with open(os.path.join(out_path, 'stdout-asp.txt'), 'w') as fp:
        fp.write(stdout)

def run_experiment(name, experiments, output, timelimit,
                   memlimit, n=1, planner=None, expgoal=False,
                   k=None, threads=1, atoms=False, track=False):
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
                                     planner=planner, expgoal=expgoal, k=k,
                                     threads=threads, atoms=atoms, track=track)
            results.append(result)
        return experiment[CALLBACK](experiment, results)

    planner = planner if planner != None else experiment[PLANNER]
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
                    k=k, n=n, threads=threads, store_effect_changes=atoms, track=track)
    
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