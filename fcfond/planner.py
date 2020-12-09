from pathlib import Path
import time
from fcfond.clingo_utils import replace_symbols
from fcfond.profile import run_profile
from fcfond.names import *

class Planner:
    def __init__(self):
        pass
    def relevant_symbols(self, domain, logdict: dict):
        pass
    def solve(self, domain, log):
        pass

class DualFondQnpPlanner(Planner):
    #FILE = Path(__file__).parent/'planner_clingo'/'planner_v2_1.lp'
    FILE = Path(__file__).parent/'planner_clingo'/'planner_v2_2.lp'

    def __init__(self):
        pass

    def relevant_symbols(self, domain, logdict: dict=None, **kwargs):
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

    def solve(self, domain, timelimit, memlimit, k=None, n=1, threads=1, **kwargs):
        k = k if k != None else 3
        args = ['clingo', DualFondQnpPlanner.FILE, domain, '-c', f'k={k}', '-n', str(n), '-t', str(threads)]
        print(args)
        return run_profile(args, time_limit=timelimit, memory_limit=memlimit)

class FairnessNoIndex(DualFondQnpPlanner):
    FILE = Path(__file__).parent/'planner_clingo'/'planner_fondp2.lp'
    def solve(self, domain, timelimit, memlimit, n=1, threads=1, **kwargs):
        args = ['clingo', FairnessNoIndex.FILE, domain, '-n', str(n), '-t', str(threads)]
        print(args)
        return run_profile(args, time_limit=timelimit, memory_limit=memlimit)

class QNPPlanner(FairnessNoIndex):
    #FILE = Path(__file__).parent/'planner_clingo'/'specialized'/'planner_qnp.lp'
    FILE = Path(__file__).parent/'planner_clingo'/'planner_fondp2.lp'
    def solve(self, domain, timelimit, memlimit, n=1, threads=1, **kwargs):
        args = ['clingo', QNPPlanner.FILE, domain, '-n', str(n), '-t', str(threads)]
        print(args)
        return run_profile(args, time_limit=timelimit, memory_limit=memlimit)

class DualFONDPlanner:
    FILE = Path(__file__).parent/'planner_clingo'/'specialized'/'planner_noindex_dual.lp'
    def solve(self, domain, timelimit, memlimit, n=1, threads=1, **kwargs):
        args = ['clingo', DualFONDPlanner.FILE, domain, '-n', str(n), '-t', str(threads)]
        print(args)
        return run_profile(args, time_limit=timelimit, memory_limit=memlimit)

class StrongPlanner:
    FILE = Path(__file__).parent/'planner_clingo'/'specialized'/'planner_strong.lp'
    def solve(self, domain, timelimit, memlimit, n=1, threads=1, **kwargs):
        args = ['clingo', StrongPlanner.FILE, domain, '-n', str(n), '-t', str(threads)]
        print(args)
        return run_profile(args, time_limit=timelimit, memory_limit=memlimit)

class StrongCyclicPlanner:
    FILE = Path(__file__).parent/'planner_clingo'/'specialized'/'planner_strongcyclic.lp'
    def solve(self, domain, timelimit, memlimit, n=1, threads=1, **kwargs):
        args = ['clingo', StrongCyclicPlanner.FILE, domain, '-n', str(n), '-t', str(threads)]
        print(args)
        return run_profile(args, time_limit=timelimit, memory_limit=memlimit)