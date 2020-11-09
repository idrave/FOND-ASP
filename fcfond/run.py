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
    FILE = Path(__file__).parent/'planner_clingo'/'planner_v2_2.lp'

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

    def solve(self, domain, k=None, n=1, **kwargs):
        k = k if k != None else 3
        args = ['clingo', FairnessPlanner.FILE, domain, '-c', f'k={k}', '-n', str(n)]
        return run_profile(args)

class FairnessNoIndex(FairnessPlanner):
    FILE = Path(__file__).parent/'planner_clingo'/'planner_noindex.lp'
    def solve(self, domain, n=1, **kwargs):
        args = ['clingo', FairnessPlanner.FILE, domain, '-n', str(n)]
        return run_profile(args)

def process_output(output, profile):
    parsed_out = parse_clingo_out(output)
    parsed_out[MAXMEM] = max(profile[MEMORY]) / 1e6
    return parsed_out

def solve_pddl(name, domain_file, problem_file, planner: Planner,
                output_dir, iterator, expand_goal=False, log=False, **kwargs):
    start = time.time()
    symbols, id_sym = encode_clingo_problem(
        domain_file, problem_file, iterator=iterator, expand_goal=expand_goal, log=log)
    logs = {'Problem': name}
    processed = str(Path(output_dir)/('proc_' + name + '.lp'))
    with open(processed, 'w') as fp:
        for symbol in symbols + id_sym:
            fp.write(str(symbol)+'.\n')
    domain_file = processed
    logs[PREPROCESS] = time.time() - start
    print('Pddl processed')
    output, profile = planner.solve(domain_file, **kwargs)
    logs.update(process_output(output, profile))
    return output, logs

def solve_clingo(name, domain_file, planner: Planner, output_dir, pre_process=False, **kwargs):
    domain_path = Path(domain_file)
    logs = {'Problem': name}
    if pre_process:
        symbols = planner.relevant_symbols(domain_file, logdict=logs) #TODO change this
        processed = str(Path(output_dir)/('proc_'+ name +'.lp'))
        with open(processed, 'w') as fp:
            for symbol in symbols:
                fp.write(str(symbol)+'.\n')
        domain_file = processed
        print('Preprocessing done')
    else:
        logs[PREPROCESS] = 0
    output, profile = planner.solve(domain_file, **kwargs)
    logs.update(process_output(output, profile))
    return output, logs

def format_results(results):
    for key, value in results.items():
        if isinstance(value, float):
            results[key] = round(value, 2)
        elif isinstance(value, bool):
            results[key] = str(value)
