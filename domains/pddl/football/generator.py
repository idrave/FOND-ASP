from fcfond.experiments import PDDL_DOM_PATHS

for i in range(3, 22, 2):
    istr = str(i).zfill(2)

    problem_str = '(define (problem football%s) (:domain footballnx2)\n' % (istr)
    problem_str += '\t(:objects %s)\n' % (' '.join('p%d'%(j) for j in range(1,i+1)))
    problem_str += '\t(:init (agent-turn) (at p%d) (defender p%d) (dist-gr0) (dec up p1) %s (dec p%d down))\n' % ((i+1)//2, (i+1)//2, ' '.join('(dec p%d p%d)'%(j,j+1) for j in range(1, i)), i)
    problem_str += '\t(:goal (not (dist-gr0)))\n'
    problem_str += '\t(:fairness\n\t\t:a (go-up down p%d p%d) (go-down p%d p%d down)\n\t\t(go-up p%d p%d up) (go-down up p%d p%d)' % (i,i-1,i-1,i,2,1,1,2)
    for j in range(1, i-1):
        problem_str += '\n\t\t(go-up p%d p%d p%d) (go-down p%d p%d p%d)' % (j+2,j+1,j,j,j+1,j+2)
    problem_str += ')\n'
    problem_str += '\t(:fairness\n\t\t:a %s\n\t\t:b %s)' % (' '.join('(go-right p%d)'%(j) for j in range(1,i+1)), ' '.join('(go-left p%d)'%(j) for j in range(1,i+1)))
    problem_str += ')'
    with open(str(PDDL_DOM_PATHS/'football'/('p%s.pddl' % (istr))), 'w') as fp:
        fp.write(problem_str)