import psutil
import multiprocessing
import subprocess
import re
import sys
import time
from fcfond.names import *

SLEEP_TIME=.0001
a = []

TIMEOUT = 'Timeout'
MEMOUT = 'Memory out'
FINISH = 'Finished'

def profile(pipe, pid, time_limit, memory_limit):
    ps = psutil.Process(pid=pid)
    mem = []
    start = time.time()
    status = FINISH
    while True:
        if ps.is_running():
            if time.time() - start > time_limit:
                status = TIMEOUT
                try:
                    ps.terminate()
                except:
                    pass
            else:
                try:
                    memory = ps.memory_info().rss
                    
                    if memory > memory_limit:
                        status = MEMOUT
                        try:
                            ps.terminate()
                        except:
                            pass
                    mem.append(memory)
                except:
                    print('Process finished')
        if pipe.poll(timeout=SLEEP_TIME):
            pipe.recv()
            break
    pipe.send({MEMORY: mem, STATUS: status})
    pipe.recv()

'''
def run_profile(args, profile=profile, time_limit=10.0, memory_limit=4e9):
    parent_conn, child_conn = multiprocessing.Pipe(duplex=True)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    prof = multiprocessing.Process(target=profile, args=(child_conn, proc.pid, time_limit, memory_limit))
    prof.start()
    child_conn.close()
    out = proc.stdout.read().decode('utf-8')
    proc.wait()
    parent_conn.send(1)
    prof_out = parent_conn.recv()
    parent_conn.send(1)
    prof.join()
    parent_conn.close()
    child_conn.close()
    return out, prof_out
'''
def run_profile(args, profile=profile, time_limit=10.0, memory_limit=4e9):
    ps = subprocess.Popen(args, stdout=subprocess.PIPE)
    proc = psutil.Process(pid=ps.pid)
    memory = []
    start = time.time()
    status = FINISH
    try:
        while True:            
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
            time.sleep(SLEEP_TIME)
            if ps.poll():
                break
    except:
        pass
    prof_out = {MEMORY: memory, STATUS: status}
    out = ps.stdout.read().decode('utf-8')
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
    args = sys.argv
    out, prof = run_profile(args[1:])
    parsed_out = parse_clingo_out(out)
    parsed_out[MAXMEM] = max(prof[MEMORY]) / 1e6
    print(parsed_out)
