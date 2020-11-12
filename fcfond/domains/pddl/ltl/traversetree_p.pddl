(define (problem trav_tree) (:domain trav_tree)
    (:init)
    (:goal (and (empty-mem) (not (has-children))))
    (:fair (select-node)))
