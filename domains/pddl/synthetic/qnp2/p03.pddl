(define (problem qnp2-03) (:domain qnp2-03)
	(:init (gr0_1) (gr0_2) (gr0_3) (p))
	(:goal (not (gr0_3)))
	(:fairness :a (a1) :b (a2))
	(:fairness :a (a2) :b (a3))
	(:fairness :a (a3))
)