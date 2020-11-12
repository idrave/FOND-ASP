(define (problem trav_list) (:domain trav_list)

    (:init (has-next))
    (:goal (not (has-next)))
    (:fair (next)))
