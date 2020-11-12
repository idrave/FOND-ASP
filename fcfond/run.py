from fcfond.profile import run_profile, parse_clingo_out, MAXMEM, MEMORY
from fondpddl import encode_clingo_problem
from fcfond.planner import Planner
import argparse
from pathlib import Path
import os
import clingo
import time
import pandas as pd
from fcfond.names import *
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
    logs = {'Problem': name}
    if pre_process:
        symbols = planner.relevant_symbols(domain_file, logdict=logs) #TODO change this (?)
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
            results[key] = round(value, 3)
        elif isinstance(value, bool):
            results[key] = str(value)
