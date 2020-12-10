(define (problem football3x2) (:domain football3x2)

    (:init (agent-turn) (at center) (defender center) (dist-gr0))

    (:goal (not (dist-gr0)))

    ;(:fair (go-up center) (go-up down) (go-down up) (go-down center))

    (:constraint
        :a (go-right up) (go-right center) (go-right down)
        :b (go-left up) (go-left center) (go-left down)))
