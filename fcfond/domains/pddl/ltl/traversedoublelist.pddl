(define (domain trav_double_list)
(:requirements :disjunctive-preconditions)

    (:predicates ;todo: define predicates here
        (at-left)
        (at-right)
        (init-left)
        (init-right))

    (:action move-left
        :parameters ()
        :precondition (not (at-left))
        :effect (oneof (at-left) (not (at-left))))

    (:action move-right
        :parameters ()
        :precondition (not (at-right))
        :effect (oneof (at-right) (not (at-right)))))