
(define (domain gripper)

    (:predicates
        (at-target)
        (balls-gr0)
        (carry-gr0)
        (empty-gr0))

    (:action drop-at-source
        :parameters ()
        :precondition (and (not (at-target)) (carry-gr0))
        :effect (and (balls-gr0) (oneof (carry-gr0) (not (carry-gr0))) (empty-gr0)))
    
    (:action drop-at-target
        :parameters ()
        :precondition (and (at-target) (carry-gr0))
        :effect (and (oneof (carry-gr0) (not (carry-gr0))) (empty-gr0)))

    (:action pick-at-source
        :parameters ()
        :precondition (and (not (at-target)) (balls-gr0) (empty-gr0))
        :effect (and (oneof (balls-gr0) (not (balls-gr0))) (carry-gr0) (oneof (empty-gr0) (not (empty-gr0)))))
    
    (:action move
        :parameters ()
        :precondition (not (at-target))
        :effect (at-target))
    
    (:action leave
        :parameters ()
        :precondition (at-target)
        :effect (not (at-target))))