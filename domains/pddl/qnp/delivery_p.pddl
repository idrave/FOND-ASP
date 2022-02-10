(define (problem delivery) (:domain delivery)
    (:init (dist-gr0)
           (targ-gr0)
           (pack-gr0))

    (:goal (and (not (holding)) (not (pack-gr0))))

    (:fairness
        :a (move)
        :b (home) (deliver))

    (:fairness
        :a (home)
        :b (move))

    (:fairness
        :a (deliver)))