from pathlib import Path
from fcfond.profile import run_profile

PLANNERPATH = Path(__file__).parent/'planner_clingo'
FONDPLUS = PLANNERPATH/'fondplus_show_pretty.lp'
FONDPSHOW = PLANNERPATH/'fondplus_show.lp'
FONDPNOSHOW = PLANNERPATH/'fondplus_noshow.lp'
INDEX = PLANNERPATH/'fondp_index.lp'
DUAL = PLANNERPATH/'specialized'/'dualfond.lp'
STRONG = PLANNERPATH/'specialized'/'planner_strong.lp'
STRONGCYCLIC = PLANNERPATH/'specialized'/'planner_strongcyclic.lp'

def solve(domain, timelimit, memlimit, k=None, n=1, threads=1, planner=None, **kwargs):
    f = FONDPLUS if planner == None else planner
    args = ['clingo', f, domain, '-n', str(n), '-t', str(threads)]
    if k != None:
        args += ['-c', f'k={k}']
    print(args)
    return run_profile(args, time_limit=timelimit, memory_limit=memlimit)