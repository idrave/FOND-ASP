(define (domain swamp_trav)
(:requirements :disjunctive-preconditions)

    (:predicates
        (empty-mem)
        (has-neigh)
        (right)
        (land))

    (:action select-node
        :parameters ()
        :precondition (and (not (empty-mem)) (not (has-neigh)))
        :effect (and (oneof (has-neigh) (not (has-neigh)))
                     (oneof (empty-mem) (not (empty-mem)))
                     (oneof (right) (not (right)))))

    (:action expand-node
        :parameters ()
        :precondition (has-neigh)
        :effect (and (not (empty-mem)) (not (has-neigh)))))