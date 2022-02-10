(define (domain membership_tree)
(:requirements :disjunctive-preconditions)
    (:predicates
        (empty-mem)
        (has-children)
        (equal))

    (:action select-node
        :parameters ()
        :precondition (and (not (empty-mem)) (not (has-children)))
        :effect (and (oneof (has-children) (not (has-children)))
                     (oneof (empty-mem) (not (empty-mem)))
                     (oneof (equal) (not (equal)))))

    (:action expand-node
        :parameters ()
        :precondition (has-children)
        :effect (and (not (empty-mem)) (not (has-children)))))