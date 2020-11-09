from pathlib import Path

PROB_NAME = 'name'
ENCODING = 'encoding'
CLINGO = 'clingo'
CLINGO_PROBLEM = 'clingo-problem'
PDDL = 'pddl'
PDDL_DOMAIN = 'pddl-domain'
PDDL_PROBLEM = 'pddl-problem'
OUTPUT = 'output'
PLANNER = 'planner'
GRAPH_ITER = 'iter'
EXP_GOAL = 'exp_goal'
PARAM_K = 'k'
EXPERIMENTS = 'experiments'

PDDL_DOM_PATHS = Path(__file__).parent.parent/'domains'/'pddl'
DEFAULT_OUT = Path(__file__).parent.parent/'res'