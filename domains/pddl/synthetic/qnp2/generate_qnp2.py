from fcfond.experiments.qnp import QNP_DOM_PATHS

for i in range(2, 11):
    istr = str(i).zfill(2)
    domain_str = '(define (domain qnp2-%s)\n' % (istr)
    domain_str += '\t(:predicates %s (p))\n' % (' '.join('(gr0_%d)' % (j+1) for j in range(i)))
    for j in range(1, i+1):
        domain_str += '\t(:action a%d\n' % (j)
        domain_str += '\t\t:parameters ()\n'
        domain_str += '\t\t:precondition (and (gr0_%d) (p)' % (j) + (' (not (gr0_%d))'%(j-1) if j > 1 else '') + ')\n'
        #domain_str += '\t\t:effect (and %s %s (not (p))))\n' % (' '.join('(gr0_%d)' % (k) for k in range(1, j)), '(oneof (gr0_%d) (not (gr0_%d)))' % (j, j))
        domain_str += '\t\t:effect (and %s %s (not (p))))\n' % ('(gr0_%d)' % (j-1) if j > 1 else '', '(oneof (gr0_%d) (not (gr0_%d)))' % (j, j))
    domain_str += '\t(:action b\n\t\t:parameters ()\n\t\t:precondition (not (p))\n\t\t:effect (p))\n)'
    with open(str(QNP_DOM_PATHS/'synthetic'/'qnp2'/('domain%s.pddl' % (istr))), 'w') as fp:
        fp.write(domain_str)

    problem_str = '(define (problem qnp2-%s) (:domain qnp2-%s)\n' % (istr, istr)
    problem_str += '\t(:init%s (p))\n' % (''.join(' (gr0_%d)' % (j) for j in range(1, i+1)))
    problem_str += '\t(:goal (not (gr0_%d)))' % (i)
    for j in range(1, i+1):
        problem_str += '\n\t(:fairness :a (a%d)%s)' % (j, ' :b (a%d)' % (j+1) if j < i else '')
        #problem_str += '\n\t(:fairness :a (a%d)' % (j)
        #if j < i:
        #    problem_str += ' :b%s' % (''.join(' (a%d)' % (k) for k in range(j+1,i+1)))
        #problem_str += ')'
    problem_str += '\n)'
    with open(str(QNP_DOM_PATHS/'synthetic'/'qnp2'/('p%s.pddl' % (istr))), 'w') as fp:
        fp.write(problem_str)
