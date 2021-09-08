from fcfond.experiments.qnp import QNP_DOM_PATHS

domain_str = '(define (domain qnp1)\n'
domain_str += '\t(:predicates (gr0 ?v) (next ?v1 ?v2) (p))\n'
domain_str += '\t(:action a\n'
domain_str += '\t\t:parameters (?v1 ?v2)\n'
domain_str += '\t\t:precondition (and (next ?v1 ?v2) (gr0 ?v2) (not (gr0 ?v1)) (p))\n'
domain_str += '\t\t:effect (and (oneof (gr0 ?v2) (not (gr0 ?v2))) (not (p))))\n'
domain_str += '\t(:action b\n'
domain_str += '\t\t:parameters ()\n'
domain_str += '\t\t:precondition (not (p))\n'
domain_str += '\t\t:effect (p)))'
with open(str(QNP_DOM_PATHS/'synthetic'/'qnp1'/'domain.pddl'), 'w') as fp:
    fp.write(domain_str)

for i in range(2, 11):
    istr = str(i).zfill(2)
    problem_str = '(define (problem qnp1-%s) (:domain qnp1)\n' % (istr)
    problem_str += '\t(:objects%s)\n' % (''.join(' v%d' % (j) for j in range(0, i+1)))
    problem_str += '\t(:init%s%s (p))\n' % (''.join(' (gr0 v%d)' % (j) for j in range(1, i+1)), ''.join(' (next v%d v%d)' % (j-1, j) for j in range(1, i+1)))
    problem_str += '\t(:goal (not (gr0 v%d)))' % (i)
    for j in range(1, i+1):
        problem_str += '\n\t(:fairness :a (a v%d v%d))' % (j-1, j)
    problem_str += '\n)'
    with open(str(QNP_DOM_PATHS/'synthetic'/'qnp1'/('p%s.pddl' % (istr))), 'w') as fp:
        fp.write(problem_str)
