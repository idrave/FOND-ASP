import subprocess
import re
import signal
import argparse
import resource
import fcfond
from fcfond.names import *

TIMEOUT = 'Timeout'
MEMOUT = 'Memory out'
FINISH = 'Finished'

def get_subprocess_memory():
    cinfo = resource.getrusage(resource.RUSAGE_CHILDREN)
    return cinfo.ru_maxrss

def limit_process_memory(nbytes):
    nbytes = int(nbytes)
    resource.setrlimit(resource.RLIMIT_AS, (nbytes, nbytes))

def is_bad_alloc(err):
    if err.find('*** ERROR: (clingo): std::bad_alloc') != -1: return True
    if err.find('MemoryError: bad_alloc') != -1: return True
    return False

def run_profile(args, time_limit=1800.0, memory_limit=8e9):
    ps = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=(lambda:limit_process_memory(memory_limit)))
    status = FINISH
    out = None
    err = None
    try:
        out, err = ps.communicate(timeout=time_limit)
    except subprocess.TimeoutExpired:
        ps.send_signal(signal.SIGINT)
        try:
            out, err = ps.communicate(timeout=1.0)
        except:
            ps.kill()
        status = TIMEOUT
    except Exception as e:
        fcfond.logger.error(e)
        pass
    out = out.decode('utf-8') if out != None else ''
    err = err.decode('utf-8') if err != None else ''
    if status == FINISH and is_bad_alloc(err):
        status = MEMOUT
    prof_out = {MEMORY: get_subprocess_memory(), STATUS: status}
    return out+err, prof_out

def parse_clingo_out(output, firstmodel=False):
    results = {}
    empty = r'\s.*?'
    answer = r'Answer: \d+?\n(.*?)\n'
    matches = re.finditer(answer, output)
    models = list(matches)
    if len(models):
        results[SAT] = True
    else:
        if output.find('UNSATISFIABLE') > -1:
            results[SAT] = False
        else:
            results[SAT] = None

    models = f'Models{empty}: (.*?)\n'
    calls = f'Calls{empty}: (.*?)\n'
    time = f'Time{empty}: (.*?)s '+r'\(Solving: (.*?)s 1st Model: (.*?)s Unsat: (.*?)s\)\n'
    cputime = f'CPU Time{empty}: (.*?)s\n'
    keys_calls = [
        (models, [(MODELS, None)]),
        (calls, [(CALLS, int)]),
        (time, [(TIME, float), (SOLVING, float), (MODEL1st, float), (TIMEUNSAT, float)]),
        (cputime, [(CPUTIME, float)])]
    
    for regex, groups in keys_calls:
        match = re.search(regex, output)
        if match == None:
            continue
        for (key, call), value in zip(groups, match.groups()):
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
