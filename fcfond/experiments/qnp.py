from fcfond.experiments.names import *
from fcfond.experiments.utils import *
from fcfond.planner import QNPPlanner

QNP_DOM_PATHS = PDDL_DOM_PATHS/'qnp'
DEFAULT_OUT_QNP = DEFAULT_OUT/'qnp'

def get_experiments():
    base_qnp = {}

    add_pddl_experiment(base_qnp, 'clear', 'clear_qnp',
                        QNP_DOM_PATHS/'clear_d.pddl', QNP_DOM_PATHS/'clear_p.pddl',
                        DEFAULT_OUT_QNP/'clear_qnp', QNPPlanner)

    add_pddl_experiment(base_qnp, 'on', 'on_qnp',
                        QNP_DOM_PATHS/'on_d.pddl', QNP_DOM_PATHS/'on_p.pddl',
                        DEFAULT_OUT_QNP/'on_qnp', QNPPlanner)

    add_pddl_experiment(base_qnp, 'gripper', 'gripper_qnp',
                        QNP_DOM_PATHS/'gripper_d.pddl', QNP_DOM_PATHS/'gripper_p.pddl',
                        DEFAULT_OUT_QNP/'gripper_qnp', QNPPlanner)

    add_pddl_experiment(base_qnp, 'delivery', 'delivery_qnp',
                        QNP_DOM_PATHS/'delivery_d.pddl', QNP_DOM_PATHS/'delivery_p.pddl',
                        DEFAULT_OUT_QNP/'delivery_qnp', QNPPlanner)

    add_experiment_list(base_qnp, 'qnp', 'qnp', list(base_qnp.keys()), DEFAULT_OUT_QNP/'all')

    unfair_qnp = {}

    add_pddl_experiment(unfair_qnp, 'clear_unfair_01', 'clear_unfair_01',
                            QNP_DOM_PATHS/'clear_d.pddl', QNP_DOM_PATHS/'clear_unfair_01.pddl',
                            DEFAULT_OUT_QNP/'clear_unfair_01', QNPPlanner)

    add_pddl_experiment(unfair_qnp, 'on_unfair_01', 'on_unfair_01',
                        QNP_DOM_PATHS/'on_d.pddl', QNP_DOM_PATHS/'on_unfair_01.pddl',
                        DEFAULT_OUT_QNP/'on_unfair_01', QNPPlanner)

    add_pddl_experiment(unfair_qnp, 'gripper_unfair_01', 'gripper_unfair_01',
                        QNP_DOM_PATHS/'gripper_d.pddl', QNP_DOM_PATHS/'gripper_unfair_01.pddl',
                        DEFAULT_OUT_QNP/'gripper_unfair_01', QNPPlanner)

    add_pddl_experiment(unfair_qnp, 'delivery_unfair_01', 'delivery_unfair_01',
                            QNP_DOM_PATHS/'delivery_d.pddl', QNP_DOM_PATHS/'delivery_unfair_01.pddl',
                            DEFAULT_OUT_QNP/'delivery_unfair_01', QNPPlanner)

    add_experiment_list(unfair_qnp, 'unfair_qnp', 'unfair_qnp', list(unfair_qnp.keys()),
                            DEFAULT_OUT_QNP/'unfair')

    sequential = {}
    for i in range(2, 11):
        si = str(i).zfill(2)
        add_pddl_experiment(sequential, 'sequential%s'%(si), 'sequential%s'%(si),
                        QNP_DOM_PATHS/'sequential'/'domain.pddl', QNP_DOM_PATHS/'sequential'/('p%s.pddl'%(si)),
                        DEFAULT_OUT_QNP/'sequential'/('p%s'%(si)), QNPPlanner)
    add_experiment_list(sequential, 'sequential', 'sequential', list(sequential.keys()), DEFAULT_OUT_QNP/'sequential'/'all')

    nested = {}
    for i in range(2, 11):
        si = str(i).zfill(2)
        add_pddl_experiment(nested, 'nested%s'%(si), 'nested%s'%(si),
                        QNP_DOM_PATHS/'nested'/('domain%s.pddl'%(si)), QNP_DOM_PATHS/'nested'/('problem%s.pddl'%(si)),
                        DEFAULT_OUT_QNP/'nested'/('p%s'%(si)), QNPPlanner)
    add_experiment_list(nested, 'nested', 'nested', list(nested.keys()), DEFAULT_OUT_QNP/'nested'/'all')

    experiments = {}
    experiments.update(base_qnp)
    experiments.update(sequential)
    experiments.update(nested)
    experiments.update(unfair_qnp)
    add_clingo_experiment(experiments, 'nested08_clingo', 'nested08_clingo', CLINGO_DOM_PATHS/'qnp'/'nested'/'nested08.lp',DEFAULT_OUT_QNP/'nested'/'p08_clingo', QNPPlanner)
    add_experiment_list(experiments, 'nested08_clingo_10reps', 'nested08_clingo_10reps', ['nested08_clingo']*10, DEFAULT_OUT_QNP/'nested'/'p08_clingo_10reps',callback=avg_results)
    add_clingo_experiment(experiments, 'nested08_simple_clingo', 'nested08_simple_clingo', CLINGO_DOM_PATHS/'qnp'/'nested'/'nested08_simple.lp',DEFAULT_OUT_QNP/'nested'/'p08_simple_clingo', QNPPlanner)
    add_experiment_list(experiments, 'nested08_simple_clingo_10reps', 'nested08_simple_clingo_10reps', ['nested08_simple_clingo']*10, DEFAULT_OUT_QNP/'nested'/'p08_simple_clingo_10reps',callback=avg_results)

    return experiments