(define (problem nestedqnp08) (:domain nestedqnp08)
	(:init (gr0_1) (gr0_2) (gr0_3) (gr0_4) (gr0_5) (gr0_6) (gr0_7) (gr0_8) (p))
	(:goal (not (gr0_8)))
	(:fairness :a (a1) :b (a2) (a3) (a4) (a5) (a6) (a7) (a8))
	(:fairness :a (a2) :b (a3) (a4) (a5) (a6) (a7) (a8))
	(:fairness :a (a3) :b (a4) (a5) (a6) (a7) (a8))
	(:fairness :a (a4) :b (a5) (a6) (a7) (a8))
	(:fairness :a (a5) :b (a6) (a7) (a8))
	(:fairness :a (a6) :b (a7) (a8))
	(:fairness :a (a7) :b (a8))
	(:fairness :a (a8)))