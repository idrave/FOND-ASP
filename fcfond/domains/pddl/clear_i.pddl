(define (problem clear) (:domain clear)
(:init (n-gr0))

(:goal (not (n-gr0)))
(:constraint
    :a (pick-above-x)
    :b (put-above-x)
)
)
