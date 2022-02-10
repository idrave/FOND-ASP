(define (domain minlist)

    (:predicates ;todo: define predicates here
        (has-next)
        (larger))

    (:action next
        :parameters ()
        :precondition (has-next)
        :effect (and (oneof (has-next) (not (has-next)))
                    (oneof (larger) (not (larger)))))

    (:action update
        :parameters ()
        :precondition (larger)
        :effect (not (larger))))