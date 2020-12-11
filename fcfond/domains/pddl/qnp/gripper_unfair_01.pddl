(define (problem gripper) (:domain gripper)
    (:init (at-target)
           (balls-gr0)
           (empty-gr0))

    (:goal (and (not (carry-gr0)) (not (balls-gr0))))

    ;(:fairness
    ;    :a (pick-at-source)
    ;    :b (drop-at-source))

    (:fairness
        :a (drop-at-source) (drop-at-target)
        :b (pick-at-source))

    (:fairness
        :a (pick-at-source)
        :b (drop-at-source) (drop-at-target)))
