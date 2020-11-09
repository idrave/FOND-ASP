import argparse
from fcfond.experiments import run_experiments

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', help='Experiment names to be run')
    parser.add_argument('-out', default=None)
    parser.add_argument('-log', action='store_true')
    parser.add_argument('-n', type=int, default=1, help='Number of policies (if 0 return all)')
    return parser.parse_args()

def main():
    args = parse_args()
    run_experiments(args.experiment, output=args.out, log=args.log, n=args.n)

if __name__ == "__main__":
    main()