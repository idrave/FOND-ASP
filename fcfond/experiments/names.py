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
EXPERIMENTS = 'experiments'
CALLBACK = 'callback'

PDDL_DOM_PATHS = Path(__file__).parent.parent/'domains'/'pddl'
CLINGO_DOM_PATHS = Path(__file__).parent.parent/'domains'/'clingo'

DEFAULT_OUT = Path(__file__).parent.parent/'res'