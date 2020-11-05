
(define (domain clear)

(:requirements :strips :negative-preconditions)

(:predicates
    (holding)
    (n-gr0)
)

(:action putaway
    :parameters ()
    :precondition (holding)
    :effect (and (and (holding)))
)

(:action pick-above-x
    :parameters ()
    :precondition (and (and (holding)) (n-gr0))
    :effect (and (holding)(and (n-gr0)(and (n-gr0))))
)

(:action put-above-x
    :parameters ()
    :precondition (holding)
    :effect (and (and (holding)) (n-gr0))
)

(:action pick-other
    :parameters ()
    :precondition (and (and (holding)))
    :effect (holding)
)


)