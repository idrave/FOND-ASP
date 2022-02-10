(define (domain sequentialqnp)

    (:predicates
        (gr0 ?v)
        (p)
        (next ?v1 ?v2))

    (:action a
        :parameters (?v1 ?v2)
        :precondition (and (next ?v1 ?v2) (gr0 ?v2) (not (gr0 ?v1)) (p))
        :effect (and (oneof (gr0 ?v2) (not (gr0 ?v2))) (not (p))))

    (:action b
        :parameters ()
        :precondition (not (p))
        :effect (p)))