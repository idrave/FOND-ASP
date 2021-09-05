from fondpddl import encode_clingo_problem, get_labeled_graph
from fondpddl.algorithm import BreadthFirstSearch
from argparse import ArgumentParser
import cProfile, pstats, io
from pstats import SortKey
import time

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('domain', help='Domain PDDL file')
    parser.add_argument('problem', help='Problem PDDL file')
    parser.add_argument('output', help='Output file for clingo symbols')
    parser.add_argument('-log', action='store_true', help='Display extra information')
    parser.add_argument('-notrack', action='store_true', help='Do not track state counting when encoding')
    parser.add_argument('-profile', action='store_true', help='Perform profiling (does not produce output file)')
    parser.add_argument('-expgoal', action='store_true', help='Whether to expand goal states')
    parser.add_argument('-graph', action='store_true', help='Output symbols as nodes and edges in labeled graph')
    args = parser.parse_args()
    if args.graph and args.expgoal:
        raise Warning('Argument \'-expgoal\' not used in option \'-graph\', which expands complete state graph')
    if args.profile:
        pr = cProfile.Profile()
        pr.enable()
        start = time.time()
        for _ in encode_clingo_problem(args.domain, args.problem, iterator=BreadthFirstSearch(), log=args.log, track=not args.track):
            pass
        print('Total Time:', time.time() - start)
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
    elif args.graph:
        with open(args.output, 'w') as fp:
            for sym in get_labeled_graph(args.domain, args.problem, iterator=BreadthFirstSearch(), log=args.log):
                fp.write(str(sym)+'.\n')
    else:
        with open(args.output, 'w') as fp:
            for sym in encode_clingo_problem(args.domain, args.problem, iterator=BreadthFirstSearch(), log=args.log, expand_goal=args.expgoal):
                fp.write(str(sym)+'.\n')
            