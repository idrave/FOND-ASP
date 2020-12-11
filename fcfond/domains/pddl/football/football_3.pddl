(define (problem football3x2) (:domain footballnx2)
    (:objects p1 p2 p3)
    (:init (agent-turn) (at p2) (defender p2) (dist-gr0)
            (dec up p1) (dec p1 p2) (dec p2 p3) (dec p3 down))

    (:goal (not (dist-gr0)))

    (:fairness
        :a (go-up down p3 p2)
           (go-up p3 p2 p1)
           (go-up p2 p1 up)
           (go-down up p1 p2)
           (go-down p1 p2 p3)
           (go-down p2 p3 down))

    (:fairness
        :a (go-right p1) (go-right p2) (go-right p3)
        :b (go-left p1) (go-left p2) (go-left p3)))
