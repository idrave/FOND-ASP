(define (problem qnp2-05) (:domain qnp2-05)
	(:init (gr0_1) (gr0_2) (gr0_3) (gr0_4) (gr0_5) (p))
	(:goal (not (gr0_5)))
	(:fairness :a (a1) :b (a2))
	(:fairness :a (a2) :b (a3))
	(:fairness :a (a3) :b (a4))
	(:fairness :a (a4) :b (a5))
	(:fairness :a (a5))
)