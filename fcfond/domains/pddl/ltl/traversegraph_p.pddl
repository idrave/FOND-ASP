(define (problem trav_graph) (:domain trav_graph)
    (:init)
    (:goal (and (empty-mem) (not (has-unmarked))))
    (:fairness :a (select-node)))
