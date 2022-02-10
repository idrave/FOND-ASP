(define (domain trav_list)

    (:predicates ;todo: define predicates here
        (has-next))

    (:action next
        :parameters ()
        :precondition (has-next)
        :effect (oneof (has-next) (not (has-next)))))