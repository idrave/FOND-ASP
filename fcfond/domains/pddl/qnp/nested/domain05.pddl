(define (domain nestedqnp05)
	(:predicates (gr0_1) (gr0_2) (gr0_3) (gr0_4) (gr0_5) (p))
	(:action a1
		:parameters ()
		:precondition (and (gr0_1) (p))
		:effect (and  (oneof (gr0_1) (not (gr0_1))) (not (p))))
	(:action a2
		:parameters ()
		:precondition (and (gr0_2) (p) (not (gr0_1)))
		:effect (and (gr0_1) (oneof (gr0_2) (not (gr0_2))) (not (p))))
	(:action a3
		:parameters ()
		:precondition (and (gr0_3) (p) (not (gr0_2)))
		:effect (and (gr0_1) (gr0_2) (oneof (gr0_3) (not (gr0_3))) (not (p))))
	(:action a4
		:parameters ()
		:precondition (and (gr0_4) (p) (not (gr0_3)))
		:effect (and (gr0_1) (gr0_2) (gr0_3) (oneof (gr0_4) (not (gr0_4))) (not (p))))
	(:action a5
		:parameters ()
		:precondition (and (gr0_5) (p) (not (gr0_4)))
		:effect (and (gr0_1) (gr0_2) (gr0_3) (gr0_4) (oneof (gr0_5) (not (gr0_5))) (not (p))))
	(:action b
		:parameters ()
		:precondition (not (p))
		:effect (p)))