from fcfond.experiments.names import *
from fcfond.experiments.utils import *

QNP_DOM_PATHS = PDDL_DOM_PATHS/'qnp'
DEFAULT_OUT_QNP = DEFAULT_OUT/'qnp'

def get_experiments():
    experiments = {}

    add_pddl_experiment(experiments, 'clear_index', 'clear_qnp_index',
                        QNP_DOM_PATHS/'clear_d.pddl', QNP_DOM_PATHS/'clear_p.pddl',
                        DEFAULT_OUT_QNP/'clear_qnp_index')

    add_pddl_experiment(experiments, 'clear', 'clear_qnp_noindex',
                        QNP_DOM_PATHS/'clear_d.pddl', QNP_DOM_PATHS/'clear_p.pddl',
                        DEFAULT_OUT_QNP/'clear_qnp_noindex', index=False)

    add_pddl_experiment(experiments, 'on_index', 'on_qnp_index',
                        QNP_DOM_PATHS/'on_d.pddl', QNP_DOM_PATHS/'on_p.pddl',
                        DEFAULT_OUT_QNP/'on_qnp_index')

    add_pddl_experiment(experiments, 'on', 'on_qnp_noindex',
                        QNP_DOM_PATHS/'on_d.pddl', QNP_DOM_PATHS/'on_p.pddl',
                        DEFAULT_OUT_QNP/'on_qnp_noindex', index=False)

    add_pddl_experiment(experiments, 'gripper_index', 'gripper_qnp_index',
                        QNP_DOM_PATHS/'on_d.pddl', QNP_DOM_PATHS/'on_p.pddl',
                        DEFAULT_OUT_QNP/'on_qnp_index')

    add_pddl_experiment(experiments, 'gripper', 'gripper_qnp_noindex',
                        QNP_DOM_PATHS/'gripper_d.pddl', QNP_DOM_PATHS/'gripper_p.pddl',
                        DEFAULT_OUT_QNP/'gripper_qnp_noindex', index=False)

    add_pddl_experiment(experiments, 'delivery_index', 'delivery_qnp_index',
                        QNP_DOM_PATHS/'delivery_d.pddl', QNP_DOM_PATHS/'delivery_p.pddl',
                        DEFAULT_OUT_QNP/'delivery_qnp_index')

    add_pddl_experiment(experiments, 'delivery', 'delivery_qnp_noindex',
                        QNP_DOM_PATHS/'delivery_d.pddl', QNP_DOM_PATHS/'delivery_p.pddl',
                        DEFAULT_OUT_QNP/'delivery_qnp_noindex', index=False)

    return experiments

def get_experiment_lists():
    return {'qnp': {EXPERIMENTS: list(get_experiments().values()), OUTPUT: DEFAULT_OUT_QNP/'all'}}