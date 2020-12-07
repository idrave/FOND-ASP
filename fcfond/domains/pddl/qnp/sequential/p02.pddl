(define (problem sequentialqnp02) (:domain sequentialqnp)
    (:objects v0 v1 v2) ; v0 always 0
    (:init
        (gr0 v1)
        (gr0 v2)
        (next v0 v1)
        (next v1 v2)
        (p))

    (:goal (not(gr0 v2)))
    (:constraint :a (a v0 v1))
    (:constraint :a (a v1 v2)))
