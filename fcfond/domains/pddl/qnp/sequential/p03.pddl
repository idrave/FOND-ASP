(define (problem sequentialqnp03) (:domain sequentialqnp)
    (:objects v0 v1 v2 v3) ; v0 always 0
    (:init
        (gr0 v1)
        (gr0 v2)
        (gr0 v3)
        (next v0 v1)
        (next v1 v2)
        (next v2 v3)
        (p))

    (:goal (not (gr0 v3)))
    (:constraint :a (a v0 v1))
    (:constraint :a (a v1 v2))
    (:constraint :a (a v2 v3)))
