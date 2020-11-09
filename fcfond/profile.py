import psutil
import multiprocessing
import subprocess
import re
import sys
import time

SLEEP_TIME=.001
MEMORY = 'Memory'
MAXMEM = 'Max Memory'
SAT = 'Sat'
MODELS = 'Models'
CALLS = 'Calls'
TIME = 'Time'
SOLVING = 'Solve Time'
MODEL1st = '1st Model Time'
TIMEUNSAT = 'Unsat Time'
CPUTIME = 'CPU Time'
a = []

def profile(pipe, pid):
    ps = psutil.Process(pid=pid)
    mem = []
    while True:
        if ps.is_running():
            try:
                mem.append(ps.memory_info().rss)
            except:
                print('Process finished')
        if pipe.poll(timeout=SLEEP_TIME):
            pipe.recv()
            break
    pipe.send({MEMORY: mem})

def run_profile(args, profile=profile):
    parent_conn, child_conn = multiprocessing.Pipe(duplex=True)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    prof = multiprocessing.Process(target=profile, args=(child_conn, proc.pid))
    prof.start()
    child_conn.close()
    out = proc.stdout.read().decode('utf-8')
    proc.wait()
    parent_conn.send(1)
    prof_out = parent_conn.recv()
    prof.join()
    parent_conn.close()
    child_conn.close()
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
