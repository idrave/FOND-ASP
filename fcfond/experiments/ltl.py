from fcfond.experiments.names import *
from fcfond.experiments.utils import *
from fcfond.planner import DualFONDPlanner, FairnessNoIndex, QNPPlanner

LTL_DOM_PATHS = PDDL_DOM_PATHS/'ltl'
DEFAULT_OUT_LTL = DEFAULT_OUT/'ltl'

def get_experiments():
    experiments = {}

    add_pddl_experiment(experiments, 'list', 'list', LTL_DOM_PATHS/'traverselist.pddl',
                        LTL_DOM_PATHS/'traverselist_p.pddl', DEFAULT_OUT_LTL/'traverselist',
                        DualFONDPlanner)

    add_pddl_experiment(experiments, 'double-list', 'double-list', LTL_DOM_PATHS/'traversedoublelist.pddl',
                        LTL_DOM_PATHS/'traversedoublelist_p.pddl', DEFAULT_OUT_LTL/'traversedoublelist',
                        QNPPlanner)
    
    add_pddl_experiment(experiments, 'tree', 'tree', LTL_DOM_PATHS/'traversetree.pddl',
                        LTL_DOM_PATHS/'traversetree_p.pddl', DEFAULT_OUT_LTL/'traversetree',
                        DualFONDPlanner)

    add_pddl_experiment(experiments, 'graph', 'graph', LTL_DOM_PATHS/'traversegraph.pddl',
                        LTL_DOM_PATHS/'traversegraph_p.pddl', DEFAULT_OUT_LTL/'traversegraph',
                        DualFONDPlanner)

    add_pddl_experiment(experiments, 'minlist', 'minlist', LTL_DOM_PATHS/'minlist.pddl',
                        LTL_DOM_PATHS/'minlist_p.pddl', DEFAULT_OUT_LTL/'minlist',
                        DualFONDPlanner)

    add_pddl_experiment(experiments, 'member-tree', 'member-tree', LTL_DOM_PATHS/'memtree.pddl',
                        LTL_DOM_PATHS/'memtree_p.pddl', DEFAULT_OUT_LTL/'memtree',
                        DualFONDPlanner)

    add_pddl_experiment(experiments, 'swamp', 'swamp', LTL_DOM_PATHS/'swamp.pddl',
                        LTL_DOM_PATHS/'swamp_p.pddl', DEFAULT_OUT_LTL/'swamp',
                        DualFONDPlanner)

    add_experiment_list(experiments, 'ltl', 'ltl', list(experiments.keys()), DEFAULT_OUT_LTL/'all')

    return experiments