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
with open(str(QNP_DOM_PATHS/'synthetic'/'qnp1_unsolvable'/'domain.pddl'), 'w') as fp:
    fp.write(domain_str)

for i in range(2, 11):
    istr = str(i).zfill(2)
    for j in range(1, 2**i):
        jstr = str(j).zfill(len(str(2**i)))
        problem_str = '(define (problem qnp1-%s) (:domain qnp1)\n' % (istr)
        problem_str += '\t(:objects%s)\n' % (''.join(' v%d' % (k) for k in range(0, i+1)))
        problem_str += '\t(:init%s%s (p))\n' % (''.join(' (gr0 v%d)' % (k) for k in range(1, i+1)), ''.join(' (next v%d v%d)' % (k-1, k) for k in range(1, i+1)))
        problem_str += '\t(:goal (not (gr0 v%d)))' % (i)
        for k in range(0, i):
            if not (j & (1 << k)):
                problem_str += '\n\t(:fairness :a (a v%d v%d))' % (k, k+1)
        problem_str += '\n)'
        with open(str(QNP_DOM_PATHS/'synthetic'/'qnp1_unsolvable'/('p%s_%s.pddl' % (istr, jstr))), 'w') as fp:
            fp.write(problem_str)
