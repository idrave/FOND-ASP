from fcfond.experiments.names import OUTPUT
from fcfond.profile import run_profile, parse_clingo_out, MAXMEM, MEMORY
from fcfond.planner import FairnessNoIndex
from fondpddl.algorithm import BreadthFirstSearch
from fondpddl import encode_clingo_problem
from fcfond.planner import Planner
import argparse
import psutil
from pathlib import Path
import os
import clingo
import time
import pandas as pd
from fcfond.names import *

def process_output(output, profile):
    print('Status: ', profile[STATUS])
    if profile[STATUS] == FINISH:
        parsed_out = parse_clingo_out(output)
        parsed_out[RESULT] = parsed_out[SAT]
    else:
        parsed_out = {RESULT: profile[STATUS]}
    parsed_out[MAXMEM] = max(profile[MEMORY]+[0]) / 1e6
    return parsed_out

def solve_pddl(name, domain_file, problem_file, planner: Planner,
                output_dir, iterator, timelimit, memlimit, expand_goal=False, log=False, **kwargs):
    start = time.time()
    logs = {PROBLEM: name}
    symbols = encode_clingo_problem(
                        domain_file, problem_file, iterator=iterator,
                        expand_goal=expand_goal, log=log, logdict=logs)
    processed = str(Path(output_dir)/('proc_' + name + '.lp'))
    process = psutil.Process(os.getpid())
    with open(processed, 'w') as fp:
        for i, symbol in enumerate(symbols):
            if i % 500 == 0:
                if time.time()-start > timelimit:
                    logs[RESULT] = TIMEOUT
                    logs[STDOUT] = f'{name}: Pre precessing timeout\n'
                    return logs
                if process.memory_info().rss > memlimit:
                    logs[RESULT] = MEMOUT
                    logs[STDOUT] = f'{name}: Pre precessing memory out\n'
                    return logs
            fp.write(str(symbol)+'.\n')
    domain_file = processed
    logs[PREPROCESS] = time.time() - start
    print('Pddl processed')
    output, profile = FairnessNoIndex().solve(domain_file, timelimit-logs[PREPROCESS], memlimit, planner=planner, **kwargs)
    logs.update(process_output(output, profile))
    logs[STDOUT] = output
    return logs

def run_pddl(pddl_files, timeout, memout, output=None, log=False, n=1, planner=None,
                    expgoal=False, k=None, threads=1):
    out_path = Path(output) if output != None else Path(OUTPUT)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)
    results = []
    for domain, problem in pddl_files:
        res = solve_pddl(Path(problem).stem, domain, problem, planner, str(out_path),
                         BreadthFirstSearch(), timeout, memout, log=log,
                         n=n, expand_goal=expgoal, k=k, threads=threads)
        format_results(res)
        results.append(res)

    stdout = ''
    for result in results:
        stdout += result[PROBLEM]+'\n'
        stdout += result[STDOUT]+'\n'
    if log:
        print(stdout)
    df = pd.DataFrame(results).drop(STDOUT, axis=1)
    df.to_csv(str(out_path/'metrics.csv'),index=False)

    if log:
        print(df)
    with open(str(out_path/'stdout.txt'), 'w') as fp:
        fp.write(stdout)

def solve_clingo(name, domain_file, planner: Planner, output_dir,
                 timelimit, memlimit, pre_process=False, **kwargs):
    logs = {PROBLEM: name}
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
    output, profile = FairnessNoIndex().solve(domain_file, timelimit, memlimit, planner=planner, **kwargs)
    logs.update(process_output(output, profile))
    logs[STDOUT] = output
    return logs

def run_clingo(clingo_files, timeout, memout, output, pre_process=False, log=False,
                n=1, planner=None, k=None, threads=1):
    
    out_path = Path(output) if output != None else Path(OUTPUT)
    if not out_path.is_dir():
        out_path.mkdir(parents=True)
    results = []
    for problem in clingo_files:
        res = solve_clingo(Path(problem).stem, problem, planner, str(output),
                         timeout, memout, log=log,
                         n=n, k=k, threads=threads)
        format_results(res)
        results.append(res)

    stdout = ''
    for result in results:
        stdout += result[PROBLEM]+'\n'
        stdout += result[STDOUT]+'\n'
    if log:
        print(stdout)
    df = pd.DataFrame(results).drop(STDOUT, axis=1)
    df.to_csv(str(out_path/'metrics.csv'),index=False)

    if log:
        print(df)
    with open(str(out_path/'stdout.txt'), 'w') as fp:
        fp.write(stdout)

def format_results(results):
    for key, value in results.items():
        if isinstance(value, float):
            results[key] = round(value, 3)
        elif isinstance(value, bool):
            results[key] = str(value)
