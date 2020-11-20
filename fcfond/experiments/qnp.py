from fcfond.experiments.names import *
from fcfond.experiments.utils import *
from fcfond.planner import QNPPlanner

QNP_DOM_PATHS = PDDL_DOM_PATHS/'qnp'
DEFAULT_OUT_QNP = DEFAULT_OUT/'qnp'

def get_experiments():
    experiments = {}

    add_pddl_experiment(experiments, 'clear', 'clear_qnp',
                        QNP_DOM_PATHS/'clear_d.pddl', QNP_DOM_PATHS/'clear_p.pddl',
                        DEFAULT_OUT_QNP/'clear_qnp', QNPPlanner)


    add_pddl_experiment(experiments, 'on', 'on_qnp',
                        QNP_DOM_PATHS/'on_d.pddl', QNP_DOM_PATHS/'on_p.pddl',
                        DEFAULT_OUT_QNP/'on_qnp', QNPPlanner)

    add_pddl_experiment(experiments, 'gripper', 'gripper_qnp',
                        QNP_DOM_PATHS/'gripper_d.pddl', QNP_DOM_PATHS/'gripper_p.pddl',
                        DEFAULT_OUT_QNP/'gripper_qnp', QNPPlanner)


    add_pddl_experiment(experiments, 'delivery', 'delivery_qnp',
                        QNP_DOM_PATHS/'delivery_d.pddl', QNP_DOM_PATHS/'delivery_p.pddl',
                        DEFAULT_OUT_QNP/'delivery_qnp', QNPPlanner)

    add_experiment_list(experiments, 'qnp', 'qnp', list(experiments.values()), DEFAULT_OUT_QNP/'all')

    return experiments