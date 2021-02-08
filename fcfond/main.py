import argparse
from fcfond.experiments import run_experiments, print_experiments
from fcfond.run import run_pddl, run_clingo
from fcfond.planner import FairnessNoIndex, StrongPlanner, StrongCyclicPlanner

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiments', nargs='*', help='Experiment names to be run')
    parser.add_argument('-pddl', nargs='+', default=None, help='PDDL files on which to run planner [as domain,problem pairs]')
    parser.add_argument('-clingo', nargs='+', default=None, help='Clingo files on which to run planner')
    parser.add_argument('-out', default=None)
    parser.add_argument('-log', action='store_true')
    parser.add_argument('--fondf', action='store_true', help='Use default FOND+ planner for all experiments')
    parser.add_argument('-planner', default=None, help='Use Clingo encoding for planner in specified path')
    parser.add_argument('--strong', action='store_true', help='Use Clingo specialized planner for pure strong planning')
    parser.add_argument('--strongcyclic', action='store_true', help='Use Clingo specialized planner for pure strong cyclic planning')
    parser.add_argument('--expgoal', action='store_true', help='Whether to expand goal states in pddl translation')
    parser.add_argument('-k', nargs='?', const='3', default=None)
    parser.add_argument('-n', type=int, default=1, help='Number of clingo models (if 0 return all)')
    parser.add_argument('-t', type=int, default=1, help='Number of threads')
    parser.add_argument('-timeout', type=float, default=1800.0, help='Timeout for each experiment')
    parser.add_argument('-memout', type=float, default=8e9, help='Memory limit for each experiment')
    return parser.parse_args()

def main():
    args = parse_args()
    '''if args.print:
        print_experiments(args.experiments)
        return'''
    if args.fondf:
        planner = FairnessNoIndex.FILE
    elif args.strong:
        planner = StrongPlanner.FILE
    elif args.strongcyclic:
        planner = StrongCyclicPlanner.FILE
    else:
        planner = args.planner
    if args.pddl != None:
        run_pddl(args.pddl, args.timeout, args.memout,
                    args.out, log=args.log,
                    n=args.n, planner=planner, expgoal=args.expgoal,
                    k=args.k, threads=args.t)
    if args.clingo != None:
        run_clingo(args.clingo, args.timeout, args.memout,
                        args.out, log=args.log,
                        n=args.n, planner=planner,
                        k=args.k, threads=args.t)
    if len(args.experiments):
        run_experiments(args.experiments, args.timeout, args.memout,
                        output=args.out, log=args.log,
                        n=args.n, planner=planner, expgoal=args.expgoal,
                        k=args.k, threads=args.t)

if __name__ == "__main__":
    main()