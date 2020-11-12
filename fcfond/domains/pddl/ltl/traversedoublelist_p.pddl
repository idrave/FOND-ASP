(define (problem trav_double_list) (:domain trav_double_list)

    (:init (oneof (and (at-left) (init-left))
                (and (at-right) (init-right))))

    (:goal (or (and (init-right) (at-left))
            (and (init-left) (at-right))))

    (:constraint
        :a (move-right)
        :b (move-left))
    (:constraint
        :a (move-left)
        :b (move-right)))
