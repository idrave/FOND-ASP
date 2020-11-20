import argparse
from fcfond.experiments import run_experiments
from fcfond.planner import FairnessNoIndex

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', help='Experiment names to be run')
    parser.add_argument('-out', default=None)
    parser.add_argument('-log', action='store_true')
    parser.add_argument('--index', action='store_true')
    parser.add_argument('--fondf', action='store_true')
    parser.add_argument('--expgoal', action='store_true', help='Whether to expand goal states in pddl translation')
    parser.add_argument('-k', nargs='?', const='3', default=None)
    parser.add_argument('-n', type=int, default=1, help='Number of policies (if 0 return all)')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.fondf:
        planner = FairnessNoIndex
    else:
        planner = None
    run_experiments(args.experiment, output=args.out, log=args.log,
                    n=args.n, planner=planner, expgoal=args.expgoal, k=args.k)

if __name__ == "__main__":
    main()