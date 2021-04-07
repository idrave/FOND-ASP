import psutil
import multiprocessing
import subprocess
import re
import sys
import time
import argparse
from fcfond.names import *

SLEEP_TIME=.001
a = []

TIMEOUT = 'Timeout'
MEMOUT = 'Memory out'
FINISH = 'Finished'

def profile(pipe, pid, time_limit, memory_limit):
    try:
        ps = psutil.Process(pid=pid)
    except:
        ps = None
    mem = []
    start = time.time()
    status = FINISH

    while True:
        if ps != None and not ps.is_running():
            try:
                if time.time() - start > time_limit:
                    status = TIMEOUT
                    ps.terminate()
                else:
                    memory = ps.memory_info().rss
                    if memory > memory_limit:
                        status = MEMOUT
                        ps.terminate()
                        mem.append(memory)
            except:
                pass
        if pipe.poll(timeout=SLEEP_TIME):
            break
    pipe.recv()
    pipe.send({MEMORY: mem, STATUS: status})
    pipe.close()
    
'''
def run_profile(args, profile=profile, time_limit=3600.0, memory_limit=4e9):
    ps = subprocess.Popen(args, stdout=subprocess.PIPE)
    parent_p, child_p = multiprocessing.Pipe(duplex=True)
    profiler = multiprocessing.Process(target=profile, args=(child_p, ps.pid, time_limit, memory_limit))    
    profiler.start()
    out = None
    try:
        out = ps.communicate()[0].decode('utf-8')
    except:
        pass #TODO
    parent_p.send(1)
    prof_out = parent_p.recv()
    profiler.join()
    child_p.close()
    parent_p.close()
    return out, prof_out'''


def run_profile(args, profile=profile, time_limit=3600.0, memory_limit=4e9):
    ps = subprocess.Popen(args, stdout=subprocess.PIPE)
    proc = psutil.Process(pid=ps.pid)
    memory = []
    start = time.time()
    status = FINISH
    out = ''
    try:
        while proc.is_running():
            if time.time() - start > time_limit:
                status = TIMEOUT
                ps.terminate()
                break
            mem = proc.memory_info().rss
            memory.append(proc.memory_info().rss)
            if mem > memory_limit:
                status = MEMOUT
                ps.terminate()
                break
            try:
                out += ps.communicate(timeout=SLEEP_TIME)[0].decode('utf-8')
            except subprocess.TimeoutExpired:
                pass
            time.sleep(SLEEP_TIME)
    except Exception as e:
        pass #TODO catch exceptions approprietly
    #if status == FINISH:
    #    out = ps.stdout.read().decode('utf-8')
    prof_out = {MEMORY: memory, STATUS: status}
    return out, prof_out

def is_sat(string):
    if string == 'SATISFIABLE':
        return True
    if string == 'UNSATISFIABLE':
        return False
    return None

def parse_clingo_out(output):
    empty = r'\s.*?'
    sat = '(SATISFIABLE|UNSATISFIABLE)\n\n'
    models = f'Models{empty}: (.*?)\n'
    calls = f'Calls{empty}: (.*?)\n'
    time = f'Time{empty}: (.*?)s '+r'\(Solving: (.*?)s 1st Model: (.*?)s Unsat: (.*?)s\)\n'
    cputime = f'CPU Time{empty}: (.*?)s\n'
    match = re.search(sat + models + calls + time + cputime, output)
    keys_calls = [
        (SAT, is_sat), (MODELS, None), (CALLS, int), (TIME, float),
        (SOLVING, float), (MODEL1st, float), (TIMEUNSAT, float), (CPUTIME, float)]
    results = {}
    for (key, call), value in zip(keys_calls, match.groups()):
        results[key] = call(value) if call != None else value
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)
    parser.add_argument('-time', type=int, default=3600)
    parser.add_argument('-mem', type=int, default=int(4e9), help='Memory limit in bytes')
    args = parser.parse_args()
    out, prof = run_profile(args.command.split(), time_limit=args.time, memory_limit=args.mem)
    print(out)
    print('Status:', prof[STATUS])
    if prof[STATUS] == FINISH:
        print('Maximum memory usage: %.2fMB' % (max(prof[MEMORY] + [0.0]) / 1e6))
