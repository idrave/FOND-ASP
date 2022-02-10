(define (domain delivery)

    (:predicates
        (holding)
        (dist-gr0)
        (targ-gr0)
        (pack-gr0))
    
    (:action move
        :parameters ()
        :precondition (dist-gr0)
        :effect (and (oneof (dist-gr0) (not (dist-gr0))) (targ-gr0)))

    (:action home
        :parameters ()
        :precondition (targ-gr0)
        :effect (and (dist-gr0) (oneof (targ-gr0) (not (targ-gr0)))))

    (:action pick
        :parameters ()
        :precondition (and (not (holding)) (not (dist-gr0)))
        :effect (holding))

    (:action drop
        :parameters ()
        :precondition (and (holding) (targ-gr0))
        :effect (not (holding)))

    (:action deliver
        :parameters ()
        :precondition (and (holding) (not (targ-gr0)) (pack-gr0))
        :effect (and (not (holding)) (dist-gr0) (oneof (pack-gr0) (not (pack-gr0))))))
