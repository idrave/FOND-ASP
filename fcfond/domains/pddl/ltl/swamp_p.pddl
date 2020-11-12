(define (problem swamp_trav) (:domain swamp_trav)
    (:init (land))
    (:goal (and (land) (or (right) (and (empty-mem) (not (has-neigh))))))
    (:fair (select-node)))
