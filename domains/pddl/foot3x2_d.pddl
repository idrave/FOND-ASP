(define (domain football3x2)
(:requirements :conditional-effects)
    (:constants
        up center down)

    (:predicates
        (agent-turn)
        (at ?pos)
        (defender ?pos)
        (dist-gr0))
        
    (:action go-right
        :parameters (?pos)
        :precondition (and (agent-turn) (dist-gr0) (at ?pos) (not (defender ?pos)))
        :effect (and (not (agent-turn)) (oneof (dist-gr0) (not (dist-gr0)))))

    (:action go-left
        :parameters (?pos)
        :precondition (and (agent-turn) (at ?pos))
        :effect (and (not (agent-turn)) (dist-gr0)))
    
    (:action go-up
        :parameters (?pos)
        :precondition (and (agent-turn) (at ?pos) (not (at up)))
        :effect (and (not (at ?pos))
                     (when (at center) (at up))
                     (when (at down) (oneof (at center) (at up)))
                     (not (agent-turn))))

    (:action go-down
        :parameters (?pos)
        :precondition (and (agent-turn) (at ?pos) (not (at down)))
        :effect (and (not (at ?pos))
                     (when (at center) (at down))
                     (when (at up) (oneof (at center) (at down)))
                     (not (agent-turn))))

    (:action defender
        :parameters (?pos)
        :precondition (and (not (agent-turn)) (defender ?pos))
        :effect (and (not (defender ?pos))
                     (when (defender up) (oneof (defender up) (defender center)))
                     (when (defender center) (oneof (defender up) (defender center) (defender down)))
                     (when (defender down) (oneof (defender center) (defender down)))
                     (agent-turn))))