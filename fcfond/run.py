from fcfond.profile import run_profile, parse_clingo_out, MAXMEM, MEMORY
from fcfond.clingo_utils import replace_symbols
from fondpddl import encode_clingo_problem
import argparse
from pathlib import Path
import os
import clingo
import time
import pandas as pd

PREPROCESS = 'Pre-processing time'

class Planner:
    def __init__(self):
        pass
    def relevant_symbols(self, domain, logdict: dict):
        pass
    def solve(self, domain, log):
        pass

class FairnessPlanner(Planner):
    #FILE = Path(__file__).parent/'planner_clingo'/'planner_v2_1.lp'
    FILE = Path(__file__).parent/'planner_clingo'/'planner_v2_1_ids.lp'

    def __init__(self):
        pass

    def relevant_symbols(self, domain, logdict: dict=None):
        if logdict != None:
            start = time.time()
        rules = (
            '#show.'
            '#show id(state(S), ID) : state(S), id(state(S), ID).'
            '#show state(ID) : state(S), id(state(S), ID).'
            '#show transition(ID1, A, ID2) : transition(S1, A, S2), id(state(S1),ID1), id(state(S2), ID2).'
            '#show initialState(ID) : initialState(S), id(state(S),ID).'
            '#show goal(ID) : goal(G), id(state(G), ID).'
            '#show action(A) : action(A).'
            '#show con_A(A,J) : con_A(A,J).'
            '#show con_B(A,J) : con_B(A,J).'
        )
        symbols = replace_symbols(domain, [('base', [])], 'state', 1, rules)
        if logdict != None:
            logdict[PREPROCESS] = time.time() - start
        return symbols

    def solve(self, domain, k=3, logdict:dict = None, **kwargs):
        args = ['clingo', FairnessPlanner.FILE, domain, '-c', f'k={k}']
        print(args)
        out, prof = run_profile(args)
        parsed_out = parse_clingo_out(out)
        parsed_out[MAXMEM] = max(prof[MEMORY]) / 1e6
        if logdict != None:
            logdict.update(parsed_out)
        return out

def solve_pddl(domain_file, problem_file, planner: Planner, output_dir, expand_goal=True, log=False, **kwargs):
    start = time.time()
    symbols, id_sym = encode_clingo_problem(domain_file, problem_file, expand_goal=expand_goal, log=log)
    logs = {'Problem': Path(problem_file).stem}
    processed = str(Path(output_dir)/('proc_' + Path(problem_file).stem + '.lp'))
    with open(processed, 'w') as fp:
        for symbol in symbols + id_sym:
            fp.write(str(symbol)+'.\n')
    domain_file = processed
    logs[PREPROCESS] = time.time() - start
    print('Pddl processed')
    output = planner.solve(domain_file, logdict=logs, **kwargs)
    return output, logs

def solve_problem(domain_file: str, planner: Planner, output_dir, pre_process=False, **kwargs):
    domain_path = Path(domain_file)
    log = {'Problem': domain_path.stem}
    #TODO should handle pddl here as well
    if pre_process:
        symbols = planner.relevant_symbols(domain_file, logdict=log)
        processed = str(Path(output_dir)/('proc_'+domain_path.stem+'.lp'))
        with open(processed, 'w') as fp:
            for symbol in symbols:
                fp.write(str(symbol)+'.\n')
        domain_file = processed
        print('Preprocessing done')
    else:
        log[PREPROCESS] = 0
    output = planner.solve(domain_file, logdict=log, **kwargs)
    return output, log

def format_results(results):
    for key, value in results.items():
        if isinstance(value, float):
            results[key] = round(value, 2)
        elif isinstance(value, bool):
            results[key] = str(value)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('problems', nargs='+')
    parser.add_argument('-out', default=None)
    parser.add_argument('-k', type=int, default=3)
    parser.add_argument('-preproc', action='store_true')
    parser.add_argument('--pddl', action='store_true')
    parser.add_argument('--log', action='store_true')
    args = parser.parse_args()
    if args.out == None:
        args.out = str(Path(__file__).parent/'res'/'default')
    return args

def run():
    args = parse_args()
    out_path = Path(args.out)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)
    df = pd.DataFrame()
    if args.pddl:
        assert len(args.problems) == 2
        output, log = solve_pddl(args.problems[0], args.problems[1], FairnessPlanner(), args.out, log=args.log, k=args.k)
        print(output)
        format_results(log)
        df = df.append(log, ignore_index=True)
    else:
        for problem in args.problems:
            output, log = solve_problem(problem, FairnessPlanner(), args.out, pre_process=args.preproc, k=args.k)
            print(problem)
            print(output)
            format_results(log)
            df = df.append(log, ignore_index=True)
    df.to_csv(str(Path(args.out)/'metrics.csv'),index=False)
    print(df.head())


if __name__ == "__main__":
    run()
