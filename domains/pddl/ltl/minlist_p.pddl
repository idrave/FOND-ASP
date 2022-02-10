(define (problem minlist) (:domain minlist)

    (:init (oneof (has-next) (not (has-next))) (larger))

    (:goal (and (not (has-next)) (not (larger))))
    (:fairness :a (next)))
