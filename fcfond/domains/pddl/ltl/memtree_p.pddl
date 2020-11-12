(define (problem membership_tree) (:domain membership_tree)
    (:init)
    (:goal (or (equal) (and (empty-mem) (not (has-children)))))
    (:fair (select-node)))
