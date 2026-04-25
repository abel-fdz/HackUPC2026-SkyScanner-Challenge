; ============================================
; HEURISTIC MODULE - DESTINATION RECOMMENDER
; ============================================

(defmodule heuristic
    (import MAIN ?ALL)
    (export ?ALL)
)

; ============================================
; INITIALIZATION
; ============================================
; Offer.score already has numeric values in our dataset.

; ============================================
; POSITIVE SCORING
; ============================================

; Apply optional offers filter created in input module.
(defrule heuristic::apply-offer-filter-price
    (declare (salience 200))
    (object (name [offers-filter]) (price ?max&~nil))
    ?of <- (object (is-a Offer)
                   (name ?name&:(neq ?name [offers-filter]))
                   (Destination ?dest&~[nil])
                   (price ?p&:(> ?p ?max)))
    =>
    (send ?of put-Destination [nil])
)

(defrule heuristic::apply-offer-filter-duration
    (declare (salience 200))
    (object (name [offers-filter]) (duration ?dur&~nil))
    ?of <- (object (is-a Offer)
                   (name ?name&:(neq ?name [offers-filter]))
                   (Destination ?dest&~[nil])
                   (duration ?d&:(<> ?d ?dur)))
    =>
    (send ?of put-Destination [nil])
)

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
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasBeach TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 25))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Beach available")
)

; Culture
(defrule heuristic::score-culture
    (object (is-a Demand) (needCulture TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasCulture TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Cultural destination")
)

; Nature
(defrule heuristic::score-nature
    (object (is-a Demand) (needNature TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasNature TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Nature environment")
)

; Mountain preference
(defrule heuristic::score-mountain
    (object (is-a Demand) (needMountain TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasMountain TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Mountain environment")
)

; Party preference
(defrule heuristic::score-party
    (object (is-a Demand) (needParty TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasParty TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Nightlife available")
)

; Activities preference
(defrule heuristic::score-activities
    (object (is-a Demand) (needActivities TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasActivities TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Activities available")
)

; History preference
(defrule heuristic::score-history
    (object (is-a Demand) (needHistory TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasHistory TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Historical sites")
)

; Climate match (if explicitly requested).
(defrule heuristic::score-climate-match
    (object (is-a Demand) (climate ?c&:(neq ?c ANY)))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasClimate ?dc&:(eq ?dc ?c)))
    =>
    (bind ?new (+ (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Preferred climate")
)

; Temperature match (if explicitly requested).
(defrule heuristic::score-temperature-match
    (object (is-a Demand) (temperature ?t&:(neq ?t ANY)))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasTemperature ?dt&:(eq ?dt ?t)))
    =>
    (bind ?new (+ (send ?of get-score) 8))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Preferred temperature")
)

; Population type match (if explicitly requested).
(defrule heuristic::score-population-match
    (object (is-a Demand) (typePopulation ?tp&:(neq ?tp ANY)))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasTypePopulation ?dp&:(eq ?dp ?tp)))
    =>
    (bind ?new (+ (send ?of get-score) 8))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Preferred destination type")
)

; Trip type alignment.
(defrule heuristic::score-trip-adventure
    (object (is-a Demand) (tripType ADVENTURE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasActivities TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Good for adventure")
)

(defrule heuristic::score-trip-relaxation
    (object (is-a Demand) (tripType RELAXATION))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasBeach TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Good for relaxation")
)

(defrule heuristic::score-trip-family
    (object (is-a Demand) (tripType FAMILY))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasActivities TRUE))
    =>
    (bind ?new (+ (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Family-friendly activities")
)

(defrule heuristic::score-trip-business
    (object (is-a Demand) (tripType BUSINESS))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasTypePopulation ?tp&:(or (eq ?tp MAJOR-CITY) (eq ?tp CITY))))
    =>
    (bind ?new (+ (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Business-friendly city")
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

; Preferred continent scoring
(defrule heuristic::score-continent-match
    (object (is-a Demand) (preferredContinent ?pc&:(neq ?pc "ANY")))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (location ?loc))
    (object (name ?loc) (continent ?c&:(eq ?c ?pc)))
    =>
    (bind ?new (+ (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Preferred continent")
)

(defrule heuristic::penalty-continent-mismatch
    (object (is-a Demand) (preferredContinent ?pc&:(neq ?pc "ANY")))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (location ?loc))
    (object (name ?loc) (continent ?c&:(neq ?c ?pc)))
    =>
    (bind ?new (- (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Different continent")
)

; Proximity scoring using computed geographic distance (km).
(defrule heuristic::score-prefer-near-very-close
    (object (is-a Demand) (proximityPreference NEAR))
    ?of <- (object (is-a Offer) (distanceFromOrigin ?d&:(<= ?d 1500.0)))
    =>
    (bind ?new (+ (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Very close to origin")
)

(defrule heuristic::score-prefer-near-medium
    (object (is-a Demand) (proximityPreference NEAR))
    ?of <- (object (is-a Offer) (distanceFromOrigin ?d&:(and (> ?d 1500.0) (<= ?d 3500.0))))
    =>
    (bind ?new (+ (send ?of get-score) 8))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Reasonably close to origin")
)

(defrule heuristic::penalty-prefer-near-far
    (object (is-a Demand) (proximityPreference NEAR))
    ?of <- (object (is-a Offer) (distanceFromOrigin ?d&:(> ?d 3500.0)))
    =>
    (bind ?new (- (send ?of get-score) 15))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Far from origin")
)

(defrule heuristic::score-prefer-far
    (object (is-a Demand) (proximityPreference FAR))
    ?of <- (object (is-a Offer) (distanceFromOrigin ?d&:(> ?d 3500.0)))
    =>
    (bind ?new (+ (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of advantages 1 "Far destination as requested")
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
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasBeach FALSE))
    =>
    (bind ?new (- (send ?of get-score) 25))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No beach")
)

; Missing culture
(defrule heuristic::penalty-no-culture
    (object (is-a Demand) (needCulture TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasCulture FALSE))
    =>
    (bind ?new (- (send ?of get-score) 20))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No cultural activities")
)

; Missing mountain
(defrule heuristic::penalty-no-mountain
    (object (is-a Demand) (needMountain TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasMountain FALSE))
    =>
    (bind ?new (- (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No mountains")
)

; Missing party
(defrule heuristic::penalty-no-party
    (object (is-a Demand) (needParty TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasParty FALSE))
    =>
    (bind ?new (- (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No nightlife")
)

; Missing activities
(defrule heuristic::penalty-no-activities
    (object (is-a Demand) (needActivities TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasActivities FALSE))
    =>
    (bind ?new (- (send ?of get-score) 12))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Few activities")
)

; Missing history
(defrule heuristic::penalty-no-history
    (object (is-a Demand) (needHistory TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasHistory FALSE))
    =>
    (bind ?new (- (send ?of get-score) 10))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "No historical sites")
)

; Climate mismatch (if explicitly requested).
(defrule heuristic::penalty-climate-mismatch
    (object (is-a Demand) (climate ?c&:(neq ?c ANY)))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasClimate ?dc&:(neq ?dc ?c)))
    =>
    (bind ?new (- (send ?of get-score) 8))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Different climate")
)

; Temperature mismatch (if explicitly requested).
(defrule heuristic::penalty-temperature-mismatch
    (object (is-a Demand) (temperature ?t&:(neq ?t ANY)))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasTemperature ?dt&:(neq ?dt ?t)))
    =>
    (bind ?new (- (send ?of get-score) 6))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Different temperature")
)

; Population mismatch (if explicitly requested).
(defrule heuristic::penalty-population-mismatch
    (object (is-a Demand) (typePopulation ?tp&:(neq ?tp ANY)))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (hasTypePopulation ?dp&:(neq ?dp ?tp)))
    =>
    (bind ?new (- (send ?of get-score) 6))
    (send ?of put-score ?new)
    (slot-insert$ ?of disadvantages 1 "Different destination type")
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
    ?of <- (object (is-a Offer) (score ?s&:(and (> ?s 60) (<= ?s 70))))
    =>
    (bind ?new (+ ?s 10))
    (send ?of put-score ?new)
)

; ============================================
; FINAL CLASSIFICATION
; ============================================

(defrule heuristic::classify
    (declare (salience -100))
    ?of <- (object (is-a Offer) (score ?s))
    =>
    (if (>= ?s 70)
        then
        (send ?of put-grade VERY_RECOMMENDED)
        (send ?of put-reason "Excellent match")
        else
        (if (>= ?s 40)
            then
            (send ?of put-grade RECOMMENDED)
            (send ?of put-reason "Good option")
            else
            (if (>= ?s 10)
                then
                (send ?of put-grade PARTIAL)
                (send ?of put-reason "Some mismatches")
                else
                (send ?of put-grade NOT_SUITABLE)
                (send ?of put-reason "Poor match"))))
)

; ============================================
; NEXT MODULE
; ============================================

(defrule heuristic::next-step
    (declare (salience -200))
    (not (object (is-a Offer) (grade nil)))
    =>
    (focus refinement)
)