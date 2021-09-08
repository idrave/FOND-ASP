(define (problem qnp1-06) (:domain qnp1)
	(:objects v0 v1 v2 v3 v4 v5 v6)
	(:init (gr0 v1) (gr0 v2) (gr0 v3) (gr0 v4) (gr0 v5) (gr0 v6) (next v0 v1) (next v1 v2) (next v2 v3) (next v3 v4) (next v4 v5) (next v5 v6) (p))
	(:goal (not (gr0 v6)))
	(:fairness :a (a v0 v1))
	(:fairness :a (a v1 v2))
	(:fairness :a (a v2 v3))
	(:fairness :a (a v3 v4))
	(:fairness :a (a v4 v5))
	(:fairness :a (a v5 v6))
)