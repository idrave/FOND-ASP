(define (domain footballnx2)
(:requirements :conditional-effects)
    (:constants
        up down)

    (:predicates
        (agent-turn)
        (at ?pos)
        (defender ?pos)
        (dist-gr0)
        (dec ?pos1 ?pos2))
        
    (:action go-right
        :parameters (?pos)
        :precondition (and (agent-turn) (dist-gr0) (at ?pos) (not (defender ?pos)))
        :effect (and (not (agent-turn)) (oneof (dist-gr0) (not (dist-gr0)))))

    (:action go-left
        :parameters (?pos)
        :precondition (and (agent-turn) (at ?pos))
        :effect (and (not (agent-turn)) (dist-gr0)))
    
    (:action go-up
        :parameters (?pos ?pos1 ?pos2)
        :precondition (and (agent-turn) (at ?pos) (dec ?pos1 ?pos) (dec ?pos2 ?pos1))
        :effect (and (not (at ?pos))
                     (not (agent-turn))
                     (when (dec up ?pos1) (at ?pos1))
                     (when (not (dec up ?pos1)) (oneof (at ?pos1) (at ?pos2)))))

    (:action go-down
        :parameters (?pos ?pos1 ?pos2)
        :precondition (and (agent-turn) (at ?pos) (dec ?pos ?pos1) (dec ?pos1 ?pos2))
        :effect (and (not (at ?pos))
                     (when (dec ?pos1 down) (at ?pos1))
                     (when (not (dec ?pos1 down)) (oneof (at ?pos1) (at ?pos2)))
                     (not (agent-turn))))

    (:action defender
        :parameters (?pos0 ?pos1 ?pos2)
        :precondition (and (not (agent-turn)) (defender ?pos1) (dec ?pos0 ?pos1) (dec ?pos1 ?pos2))
        :effect (and (not (defender ?pos1))
                     (when (dec up ?pos1) (oneof (defender ?pos1) (defender ?pos2)))
                     (when (not (or (dec up ?pos1) (dec ?pos1 down))) (oneof (defender ?pos0) (defender ?pos1) (defender ?pos2)))
                     (when (dec ?pos1 down) (oneof (defender ?pos1) (defender ?pos0)))
                     (agent-turn))))