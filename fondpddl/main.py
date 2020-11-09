from fondpddl import encode_clingo_problem
from fondpddl.algorithm import BreadthFirstSearch
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('domain')
    parser.add_argument('problem')
    parser.add_argument('-log', action='store_true')
    args = parser.parse_args()
    symbols, ids = encode_clingo_problem(args.domain, args.problem, iterator=BreadthFirstSearch(), log=args.log)
    for sym in symbols + ids:
        print(sym)