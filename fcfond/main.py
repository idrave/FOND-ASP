import argparse
from fcfond.experiments import run_experiments, print_experiments
from fcfond.planner import FairnessNoIndex

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiments', nargs='+', help='Experiment names to be run')
    parser.add_argument('-out', default=None)
    parser.add_argument('-log', action='store_true')
    parser.add_argument('--index', action='store_true')
    parser.add_argument('--fondf', action='store_true')
    parser.add_argument('--expgoal', action='store_true', help='Whether to expand goal states in pddl translation')
    parser.add_argument('-k', nargs='?', const='3', default=None)
    parser.add_argument('-n', type=int, default=1, help='Number of clingo models (if 0 return all)')
    parser.add_argument('-t', type=int, default=1, help='Number of threads')
    parser.add_argument('-timeout', type=float, default=3600.0, help='Timeout for each experiment')
    parser.add_argument('-memout', type=float, default=4e9, help='Memory limit for each experiment')
    parser.add_argument('--print', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.print:
        print_experiments(args.experiments)
        return
    if args.fondf:
        planner = FairnessNoIndex
    else:
        planner = None
    run_experiments(args.experiments, args.timeout, args.memout,
                    output=args.out, log=args.log,
                    n=args.n, planner=planner, expgoal=args.expgoal,
                    k=args.k, threads=args.t)

if __name__ == "__main__":
    main()