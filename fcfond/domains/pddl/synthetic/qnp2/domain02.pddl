(define (domain qnp2-02)
	(:predicates (gr0_1) (gr0_2) (p))
	(:action a1
		:parameters ()
		:precondition (and (gr0_1) (p))
		:effect (and  (oneof (gr0_1) (not (gr0_1))) (not (p))))
	(:action a2
		:parameters ()
		:precondition (and (gr0_2) (p) (not (gr0_1)))
		:effect (and (gr0_1) (oneof (gr0_2) (not (gr0_2))) (not (p))))
	(:action b
		:parameters ()
		:precondition (not (p))
		:effect (p))
)