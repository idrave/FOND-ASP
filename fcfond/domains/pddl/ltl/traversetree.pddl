(define (domain trav_tree)

    (:predicates
        (empty-mem)
        (has-children))

    (:action select-node
        :parameters ()
        :precondition (and (not (empty-mem)) (not (has-children)))
        :effect (and (oneof (has-children) (not (has-children)))
                    (oneof (empty-mem) (not (empty-mem)))))

    (:action expand-node
        :parameters ()
        :precondition (has-children)
        :effect (and (not (empty-mem)) (not (has-children)))))