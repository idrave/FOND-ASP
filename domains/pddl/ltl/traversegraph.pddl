(define (domain trav_graph)

    (:predicates
        (empty-mem)
        (has-unmarked))

    (:action select-node
        :parameters ()
        :precondition (and (not (empty-mem)) (not (has-unmarked)))
        :effect (and (oneof (has-unmarked) (not (has-unmarked)))
                    (oneof (empty-mem) (not (empty-mem)))))

    (:action put-unmarked
        :parameters ()
        :precondition (has-unmarked)
        :effect (and (not (empty-mem)) (not (has-unmarked)))))