from fcfond.experiments.names import *
from fcfond.experiments.utils import *
import fcfond.planner

SYNTHETIC_DOM_PATHS = PDDL_DOM_PATHS/'synthetic'
DEFAULT_OUT_SYNTHETIC = DEFAULT_OUT/'synthetic'

def get_experiments():
    experiments = {}
    qnp1 = []
    qnp2 = []
    for i in range(2,11):
        name = 'qnp1_%.2d'%i
        add_pddl_experiment(experiments, name, name,
                            SYNTHETIC_DOM_PATHS/'qnp1'/'domain.pddl', SYNTHETIC_DOM_PATHS/'qnp1'/('p%.2d.pddl'%i),
                            DEFAULT_OUT_SYNTHETIC/name, fcfond.planner.FONDPLUS)
        qnp1.append(name)
        name = 'qnp2_%.2d'%i
        add_pddl_experiment(experiments, name, name,
                            SYNTHETIC_DOM_PATHS/'qnp2'/('domain%.2d.pddl'%i), SYNTHETIC_DOM_PATHS/'qnp2'/('p%.2d.pddl'%i),
                            DEFAULT_OUT_SYNTHETIC/name, fcfond.planner.FONDPLUS)
        qnp2.append(name)

    add_experiment_list(experiments, 'synth_qnp1', 'synth_qnp1', qnp1, DEFAULT_OUT_SYNTHETIC/'qnp1_all')
    add_experiment_list(experiments, 'synth_qnp2', 'synth_qnp2', qnp2, DEFAULT_OUT_SYNTHETIC/'qnp2_all')
    return experiments