(define (problem delivery) (:domain delivery)
    (:init (dist-gr0)
           (targ-gr0)
           (pack-gr0))

    (:goal (and (not (holding)) (not (pack-gr0))))

    (:constraint
        :a (move)
        :b (home) (deliver))

    (:constraint
        :a (home)
        :b (move))

    (:constraint
        :a (deliver)))