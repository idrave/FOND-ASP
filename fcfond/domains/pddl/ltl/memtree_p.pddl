(define (problem membership_tree) (:domain membership_tree)
    (:init)
    (:goal (or (equal) (and (empty-mem) (not (has-children)))))
    (:fairness :a (select-node)))
