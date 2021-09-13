import argparse
import fondpddl
from fcfond.experiments.names import OUTPUT
from fcfond.experiments import run_experiments, list_experiments
from fcfond.run import run_pddl, run_clingo
import fcfond.planner
from pathlib import Path
import logging
import re
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiments', nargs='*',
                        help='Experiment names to be run')
    parser.add_argument('-list', nargs='?', const='', default=None,
                        help='Display contents of a list of experiments. If none specified, show a list of options.')
    parser.add_argument('-pddl', nargs='+', default=None,
                        help='PDDL files on which to run planner [as domain-problem pairs in sequence]')
    parser.add_argument('-clingo', nargs='+', default=None,
                        help='Clingo files on which to run planner')
    parser.add_argument('-out', default=None, help='Output folder')
    parser.add_argument('-log', action='store_true',
                        help='Print additional information')
    parser.add_argument('-notrack', action='store_true', help='Do not track state counting when encoding')
    parser.add_argument('-stats', action='store_true',
                        help='Print stats information')
    group_planner = parser.add_mutually_exclusive_group()
    group_planner.add_argument('-planner', default=None, dest='planner',
                        help='Use Clingo encoding for planner in specified path')
    group_planner.add_argument('--fondp', action='store_const', const=fcfond.planner.FONDPLUS, dest='planner',
                        help='Use default FOND+ planner with conditional fairness')
    group_planner.add_argument('--fondpshow', action='store_const', const=fcfond.planner.FONDPSHOW, dest='planner',
                        help='Use default FOND+ planner with simple show statements')
    group_planner.add_argument('--fondpnoshow', action='store_const', const=fcfond.planner.FONDPNOSHOW, dest='planner',
                        help='Use default FOND+ planner without show statements')
    group_planner.add_argument('--strong', action='store_const', const=fcfond.planner.STRONG, dest='planner',
                        help='Use Clingo specialized planner for pure strong planning')
    group_planner.add_argument('--strongcyclic', action='store_const', const=fcfond.planner.STRONGCYCLIC, dest='planner',
                        help='Use Clingo specialized planner for pure strong cyclic planning')
    group_planner.add_argument('--dual', action='store_const', const=fcfond.planner.DUAL, dest='planner',
                        help='Use Clingo specialized planner for DualFOND planning')
    group_planner.add_argument('--index', action='store_const', const=fcfond.planner.INDEX, dest='planner',
                        help='Use Clingo specialized planner for DualFOND planning')
    parser.add_argument('-k', type=int, default=3,
                        help='Index limit for planner with option --index (default: %(default)s)')
    parser.add_argument('--expgoal', action='store_true',
                        help='Whether to expand goal states in pddl translation')
    parser.add_argument('-n', type=int, default=1,
                        help='Number of clingo models; 0 to return all (default: %(default)s)')
    parser.add_argument('-t', type=int, default=1, help='Number of threads')
    parser.add_argument('-timeout', type=float, default=1800.0,
                        help='Timeout for each experiment in seconds (default: %(default)s)')
    parser.add_argument('-memout', type=str, default="8G",
                        help='Memory limit for each experiment in bytes (suffix M/G for Megabytes/Gigabytes) (default: %(default)s)')
    args = parser.parse_args()

    # process args.memout in case it is given human notation xxG or xxM
    try:
        mem = float(args.memout)    # memout is just bytes
    except: # memout must have an M or G
        try:
            search_mem = re.search("(.*?)([GM])", args.memout) 
            mem = float(search_mem.group(1))
            if search_mem.group(2) == "G":
                mem = mem * 1000000000
            elif search_mem.group(2) == "M":
                mem = mem * 1000000
        except Exception as e:
            print("Problem with memory specification. Use float with optional M and G suffix: ", e)
            exit(1)
    args.memout = mem  

    if args.planner != fcfond.planner.INDEX:
        args.k = None
    return args


def main():
    args = parse_args()
    print(args)
    if args.list != None:
        list_experiments(args.list)
        return

    outpath = Path(args.out if args.out != None else OUTPUT)
    if not outpath.is_dir():
        outpath.mkdir(parents=True)
    logging.basicConfig(level=logging.DEBUG if args.log else logging.INFO,
                        handlers=[logging.StreamHandler(sys.stdout)],
                        format='%(message)s')
    fondpddl.logger.addHandler(logging.FileHandler(outpath/'stdout-encode.txt','w'))

    planner = args.planner
    if args.pddl != None:
        assert len(args.pddl) % 2 == 0, "Must have an even number of pddl files"
        pddls = [args.pddl[i:i+2] for i in range(0,len(args.pddl),2)]
        run_pddl(pddls, args.timeout, args.memout,
                    args.out, track=not args.notrack, stats=args.stats,
                    n=args.n, planner=planner, expgoal=args.expgoal,
                    k=args.k, threads=args.t)
    if args.clingo != None:
        run_clingo(args.clingo, args.timeout, args.memout,
                        args.out, stats=args.stats,
                        n=args.n, planner=planner,
                        k=args.k, threads=args.t)
    if len(args.experiments):
        run_experiments(args.experiments, args.timeout, args.memout,
                        output=args.out, stats=args.stats,
                        n=args.n, planner=planner, expgoal=args.expgoal,
                        k=args.k, threads=args.t)

if __name__ == "__main__":
    main()
