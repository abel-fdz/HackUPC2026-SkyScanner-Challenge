; ============================================
; HEURISTIC MODULE - DESTINATION RECOMMENDER
; ============================================

(defmodule heuristic
    (import MAIN ?ALL)
    (export ?ALL)
)

; ============================================
; INITIALIZATION (ensure score starts at 0)
; ============================================

(defrule heuristic::init-score
    ?of <- (object (is-a Offer) (score ?s&:(neq ?s 0.0)))
    =>
    (send ?of put-score 0.0)
)

; ============================================
; POSITIVE SCORING
; ============================================

; Budget OK
(defrule heuristic::score-budget-good
    (object (is-a Demand) (budgetMax ?bMax))
    ?of <- (object (is-a Offer) (price ?p&:(<= ?p ?bMax)))
    =>
    (bind ?new (+ (send ?of get-score) 30))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Within budget")
)

; Beach preference
(defrule heuristic::score-beach
    (object (is-a Demand) (needBeach TRUE))
    ?of <- (object (is-a Offer) (hasBeach TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 25))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Beach available")
)

; Culture
(defrule heuristic::score-culture
    (object (is-a Demand) (needCulture TRUE))
    ?of <- (object (is-a Offer) (hasCulture TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Cultural destination")
)

; Nature
(defrule heuristic::score-nature
    (object (is-a Demand) (needNature TRUE))
    ?of <- (object (is-a Offer) (hasNature TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Nature environment")
)

; Short trip compatibility
(defrule heuristic::score-short-trip
    (object (is-a Demand) (durationLevel SHORT))
    ?of <- (object (is-a Offer) (travelTime SHORT))
    =>
    (bind ?new (+ (send ?of get-score) 15))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Good for short trips")
)

; ============================================
; NEGATIVE SCORING
; ============================================

; Too expensive
(defrule heuristic::penalty-expensive
    (object (is-a Demand) (budgetMax ?bMax))
    ?of <- (object (is-a Offer) (price ?p&:(> ?p ?bMax)))
    =>
    (bind ?new (- (send ?of get-score) 40))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Over budget")
)

; Missing beach
(defrule heuristic::penalty-no-beach
    (object (is-a Demand) (needBeach TRUE))
    ?of <- (object (is-a Offer) (hasBeach FALSE))
    =>
    (bind ?new (- (send ?of get-score) 25))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No beach")
)

; Missing culture
(defrule heuristic::penalty-no-culture
    (object (is-a Demand) (needCulture TRUE))
    ?of <- (object (is-a Offer) (hasCulture FALSE))
    =>
    (bind ?new (- (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No cultural activities")
)

; Too far for short trip
(defrule heuristic::penalty-distance
    (object (is-a Demand) (durationLevel SHORT))
    ?of <- (object (is-a Offer) (travelTime LONG))
    =>
    (bind ?new (- (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Too far")
)

; ============================================
; SMART INTERACTIONS (ADVANCED)
; ============================================

; Low budget + expensive destination
(defrule heuristic::penalty-low-budget
    (object (is-a Demand) (budgetLevel LOW))
    ?of <- (object (is-a Offer) (priceLevel HIGH))
    =>
    (bind ?new (- (send ?of get-score) 30))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Too expensive for low budget")
)

; High match bonus
(defrule heuristic::bonus-high-score
    ?of <- (object (is-a Offer) (score ?s&:(> ?s 60)))
    =>
    (bind ?new (+ ?s 10))
    (send ?of put-score ?new)
)

; ============================================
; FINAL CLASSIFICATION
; ============================================

(defrule heuristic::classify
    (declare (salience -10))
    ?of <- (object (is-a Offer) (score ?s) (grade nil))
    =>
    (if (>= ?s 70) then
        (send ?of put-grade VERY_RECOMMENDED)
        (send ?of put-reason "Excellent match")
    else if (>= ?s 40) then
        (send ?of put-grade RECOMMENDED)
        (send ?of put-reason "Good option")
    else if (>= ?s 10) then
        (send ?of put-grade PARTIAL)
        (send ?of put-reason "Some mismatches")
    else
        (send ?of put-grade NOT_SUITABLE)
        (send ?of put-reason "Poor match")
    )
)

; ============================================
; NEXT MODULE
; ============================================

(defrule heuristic::next-step
    (declare (salience -20))
    =>
    (focus refinement)
)