(define (problem football6x2) (:domain footballnx2)
    (:objects p1 p2 p3 p4 p5 p6)
    (:init (agent-turn) (at p3) (defender p3) (dist-gr0)
            (dec up p1) (dec p1 p2) (dec p2 p3) (dec p3 p4) (dec p4 p5) (dec p5 p6) (dec p6 down))

    (:goal (not (dist-gr0)))

    (:fairness :a (go-up down p6 p5)
           (go-up p6 p5 p4)
           (go-up p5 p4 p3)
           (go-up p4 p3 p2)
           (go-up p3 p2 p1)
           (go-up p2 p1 up)
           (go-down up p1 p2)
           (go-down p1 p2 p3)
           (go-down p2 p3 p4)
           (go-down p3 p4 p5)
           (go-down p4 p5 p6)
           (go-down p5 p6 down))

    (:fairness
        :a (go-right p1) (go-right p2) (go-right p3) (go-right p4) (go-right p5) (go-right p6)
        :b (go-left p1) (go-left p2) (go-left p3) (go-left p4) (go-left p5) (go-left p6)))
