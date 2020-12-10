(define (problem clear) (:domain clear)
    (:init (n-gr0))
    (:goal (not (n-gr0))) ; constraints ((pick-above-x), (put-above-x))
    )