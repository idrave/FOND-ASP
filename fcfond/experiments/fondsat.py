from fcfond.experiments.names import *
from fcfond.experiments.utils import *
from fcfond.planner import StrongPlanner, StrongCyclicPlanner

FONDSAT_DOM_PATHS = PDDL_DOM_PATHS/'fond-sat'
DEFAULT_OUT_FONDSAT = DEFAULT_OUT/'fond-sat'

def get_fond_sat_experiments(name, nums):
    domain_path = FONDSAT_DOM_PATHS/name/'domain.pddl'
    strong_problem_path = FONDSAT_DOM_PATHS/name/'strong'
    cyclic_problem_path = FONDSAT_DOM_PATHS/name/'cyclic'
    strong_out = DEFAULT_OUT_FONDSAT/name/'strong'
    cyclic_out = DEFAULT_OUT_FONDSAT/name/'cyclic'
    
    f = 1
    all_strong = {}
    all_cyclic = {}
    for i, num in enumerate(nums):
        strong_exp = {}
        cyclic_exp = {}
        for p in range(f, f+num):
            prob = 'p' + str(p).zfill(2)
            print(prob)
            prob_name = name + '_' + prob
            add_pddl_experiment(strong_exp, prob_name+'_strong', prob_name+'_strong', domain_path,
                                strong_problem_path/(prob+'.pddl'), strong_out/prob,
                                StrongPlanner)
            add_pddl_experiment(cyclic_exp, prob_name+'_cyclic', prob_name+'_cyclic', domain_path,
                                cyclic_problem_path/(prob+'.pddl'), cyclic_out/prob,
                                StrongCyclicPlanner)
        strong_list = name + '_l' + str(i) + '_strong'
        cyclic_list = name + '_l' + str(i) + '_cyclic'
        add_experiment_list(strong_exp, strong_list, strong_list,
                            list(strong_exp.keys()), strong_out/('l'+str(i)),callback=avg_results)
        add_experiment_list(cyclic_exp, cyclic_list, cyclic_list,
                            list(cyclic_exp.keys()), cyclic_out/('l'+str(i)),callback=avg_results)
        all_strong.update(strong_exp)
        all_cyclic.update(cyclic_exp)
        f += num
    return all_strong, all_cyclic

def get_experiments():
    experiments = {}

    domains = [('elevators', [10, 5], True)]
    all_fondsat = []
    for name, nums, strong in domains:
        strong, cyclic = get_fond_sat_experiments(name, nums)
        experiments.update(strong)
        experiments.update(cyclic)
        all_fondsat.append(cyclic)
        if strong:
            all_fondsat.append(strong)
    
    add_experiment_list(experiments, 'fond_sat', 'fond_sat', all_fondsat, DEFAULT_OUT_FONDSAT/'all')
    return experiments