import psutil
import threading, queue
import subprocess
import re
import sys
import time
import argparse
import resource
from fcfond.names import *

SLEEP_TIME=.001
a = []

TIMEOUT = 'Timeout'
MEMOUT = 'Memory out'
FINISH = 'Finished'

def mem_profile(q, pid):
    try:
        ps = psutil.Process(pid=pid)
    except:
        ps = None
    memory = 0.0

    while ps != None and ps.is_running():
        try:
            memory = max(memory,ps.memory_info().rss)
        except:
            pass
        time.sleep(SLEEP_TIME)
    q.put(memory)

def get_subprocess_memory():
    cinfo = resource.getrusage(resource.RUSAGE_CHILDREN)
    return cinfo.ru_maxrss

def limit_process_memory(bytes):
    resource.setrlimit(resource.RLIMIT_AS, (bytes, bytes))

def run_profile(args, time_limit=3600.0, memory_limit=4e9):
    ps = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=(lambda:limit_process_memory(memory_limit)))
    q = queue.Queue()
    t = threading.Thread(target=mem_profile,args=[q,ps.pid])
    t.start()
    status = FINISH
    out = ''
    try:
        out, err = ps.communicate(timeout=time_limit)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        if err.find("MemoryError: std::bad_alloc")!=-1:
            status = MEMOUT
    except subprocess.TimeoutExpired:
        ps.send_signal(signal.SIGINT)
        try:
            out = ps.communicate(timeout=1.0)[0].decode('utf-8')
        except:
            ps.kill()
        status = TIMEOUT
    except Exception as e:
        print(e)
        pass
    print(status)
    mem = q.get()
    t.join()
    prof_out = {MEMORY: mem, STATUS: status}
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
    vals = match.groups() if match != None else [None] * len(keys_calls)
    for (key, call), value in zip(keys_calls, match.groups()):
        if value == None:
            results[key] = None
        else:
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
