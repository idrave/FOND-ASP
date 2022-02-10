(define (problem clear) (:domain on-block)
    (:init (empty)
           (n-gr0)
           (m-gr0))
    (:goal (goal)) 
    (:fairness
        :a (pick-above-x))
    (:fairness
        :a (pick-above-y)
        :b (put-x-on-y)))
