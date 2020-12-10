(define (problem clear) (:domain on-block)
    (:init (empty)
           (n-gr0)
           (m-gr0))
    (:goal (goal)) 
    (:constraint
        :a (pick-above-x))
    ;(:constraint
    ;    :a (pick-above-y)
    ;    :b (put-x-on-y))
    )

; constraints ((pick-above-y), ())
; constraints ((put-x-on-y), ())