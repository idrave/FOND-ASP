
(define (domain CLEAR)

(:requirements :strips :negative-preconditions)

(:predicates
    (holding)
    (n-gr0)
)

(:action putaway
    :parameters ()
    :precondition (holding)
    :effect (not (holding))
)

(:action pick-above-x
    :parameters ()
    :precondition (and (not (holding)) (n-gr0))
    :effect (and (holding)(oneof (n-gr0)(not (n-gr0))))
)

(:action put-above-x
    :parameters ()
    :precondition (holding)
    :effect (and (not (holding)) (n-gr0))
)

(:action pick-other
    :parameters ()
    :precondition (not (holding))
    :effect (holding)
)


)