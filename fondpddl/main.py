from fondpddl import encode_clingo_problem
from fondpddl.algorithm import BreadthFirstSearch
from argparse import ArgumentParser
import cProfile, pstats, io
from pstats import SortKey
import time

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('domain')
    parser.add_argument('problem')
    parser.add_argument('-log', action='store_true')
    parser.add_argument('-profile', action='store_true')
    parser.add_argument('-expgoal', action='store_true')
    args = parser.parse_args()
    if args.profile:
        pr = cProfile.Profile()
        pr.enable()
        start = time.time()
        encode_clingo_problem(args.domain, args.problem, iterator=BreadthFirstSearch(), log=args.log)
        print('Total Time:', time.time() - start)
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
    else:
        symbols, ids = encode_clingo_problem(args.domain, args.problem, iterator=BreadthFirstSearch(), log=args.log, expand_goal=args.expgoal)
        for sym in symbols + ids:
            print(str(sym)+'.')