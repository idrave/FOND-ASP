(define (domain on-block)
    (:predicates
        (empty)
        (hold-x)
        (goal)
        (n-gr0)
        (m-gr0))
        
    (:action pick-x
        :parameters ()
        :precondition (and (empty) (not (n-gr0)))
        :effect (and (not (empty)) (hold-x)))

    (:action pick-above-x
        :parameters ()
        :precondition (and (empty) (n-gr0))
        :effect (and (not (empty)) (oneof (n-gr0) (not (n-gr0)))))
    
    (:action pick-above-y
        :parameters ()
        :precondition (and (empty) (m-gr0))
        :effect (and (not (empty)) (oneof (m-gr0) (not (m-gr0)))))
    
    (:action putaside
        :parameters ()
        :precondition (and (not (empty)) (not (hold-x)))
        :effect (empty))
    
    (:action put-x-aside
        :parameters ()
        :precondition (and (not (empty)) (hold-x))
        :effect (and (empty) (not (hold-x))))

    (:action put-x-on-y
        :parameters ()
        :precondition (and (not (empty)) (hold-x) (not (m-gr0)))
        :effect (and (empty) (not (hold-x)) (goal) (m-gr0))))