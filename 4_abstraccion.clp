;;; Módulo de abstracción: deriva características y evalúa ofertas

(defmodule abstraction
    (import MAIN ?ALL)
    (export ?ALL)
)

;;; Funciones auxiliares

; Calcula la distancia en metros entre dos puntos geográficos.
(deffunction distance-meters (?lat1 ?lon1 ?lat2 ?lon2)
   (bind ?dLat (* (- ?lat1 ?lat2) 111000))
   (bind ?dLon (* (- ?lon1 ?lon2) (* 111000 (cos (* ?lat1 0.01745329252)))))
   (sqrt (+ (* ?dLat ?dLat) (* ?dLon ?dLon)))
)

; Distance in kilometers, used by heuristics and output.
(deffunction distance-km (?lat1 ?lon1 ?lat2 ?lon2)
   (return (/ (distance-meters ?lat1 ?lon1 ?lat2 ?lon2) 1000.0))
)

; Smallest circular month distance (e.g. DEC->JAN = 1).
(deffunction month-distance (?m1 ?m2)
   (bind ?d (abs (- ?m1 ?m2)))
   (if (> ?d 6)
      then (return (- 12 ?d))
      else (return ?d))
)

; IF budgetMax < 1000 THEN budgetLevel = LOW
(defrule abstraction::derive-budget-low
    ?d <- (object (is-a Demand) (budgetMax ?p&:(< ?p 1000)) (budgetLevel nil))
    =>
    (send ?d put-budgetLevel LOW)
)

; IF budgetMax between 1000-2000 THEN budgetLevel = LOW_MEDIUM
(defrule abstraction::derive-budget-low-medium
    ?d <- (object (is-a Demand) (budgetMax ?p&:(and (>= ?p 1000) (< ?p 2000))) (budgetLevel nil))
    =>
    (send ?d put-budgetLevel LOW_MEDIUM)
)

; IF budgetMax between 2000-4000 THEN budgetLevel = MEDIUM
(defrule abstraction::derive-budget-medium
    ?d <- (object (is-a Demand) (budgetMax ?p&:(and (>= ?p 2000) (< ?p 4000))) (budgetLevel nil))
    =>
    (send ?d put-budgetLevel MEDIUM)
)

; IF budgetMax between 4000-8000 THEN budgetLevel = MEDIUM_HIGH
(defrule abstraction::derive-budget-medium-high
    ?d <- (object (is-a Demand) (budgetMax ?p&:(and (>= ?p 4000) (< ?p 8000))) (budgetLevel nil))
    =>
    (send ?d put-budgetLevel MEDIUM_HIGH)
)

; IF budgetMax between 8000-16000 THEN budgetLevel = HIGH
(defrule abstraction::derive-budget-high
    ?d <- (object (is-a Demand) (budgetMax ?p&:(and (>= ?p 8000) (< ?p 16000))) (budgetLevel nil))
    =>
    (send ?d put-budgetLevel HIGH)
)

; IF budgetMax >= 16000 THEN budgetLevel = UNLIMITED
(defrule abstraction::derive-budget-unlimited
    ?d <- (object (is-a Demand) (budgetMax ?p&:(>= ?p 16000)) (budgetLevel nil))
    =>
    (send ?d put-budgetLevel UNLIMITED)
)

; IF tripDuration < 7 THEN durationLevel = SHORT
(defrule abstraction::derive-duration-short
    ?d <- (object (is-a Demand) (tripDuration ?t&:(< ?t 7)) (durationLevel nil))
    =>
    (send ?d put-durationLevel SHORT)
)

; IF tripDuration between 7-14 THEN durationLevel = MEDIUM
(defrule abstraction::derive-duration-medium
    ?d <- (object (is-a Demand) (tripDuration ?t&:(and (>= ?t 7) (< ?t 14))) (durationLevel nil))
    =>
    (send ?d put-durationLevel MEDIUM)
)

; IF tripDuration between 14-21 THEN durationLevel = LONG
(defrule abstraction::derive-duration-long
    ?d <- (object (is-a Demand) (tripDuration ?t&:(and (>= ?t 14) (< ?t 21))) (durationLevel nil))
    =>
    (send ?d put-durationLevel LONG)
)

; IF tripDuration between 22-30 THEN durationLevel = VERY_LONG
(defrule abstraction::derive-duration-very-long
    ?d <- (object (is-a Demand) (tripDuration ?t&:(and (>= ?t 22) (< ?t 30))) (durationLevel nil))
    =>
    (send ?d put-durationLevel VERY_LONG)
)

; IF tripDuration > 30 THEN durationLevel = EXTENDED
(defrule abstraction::derive-duration-extended
    ?d <- (object (is-a Demand) (tripDuration ?t&:(> ?t 30)) (durationLevel nil))
    =>
    (send ?d put-durationLevel EXTENDED)
)

;; Beach
; IF needBeach = FALSE THEN beach-ok = YES
(defrule abstraction::beach-not-needed
    (object (is-a Demand) (needBeach FALSE))
    ?of <- (object (is-a Offer) (beach-ok nil))
    =>
    (send ?of put-beach-ok YES)
)

; IF needBeach = TRUE AND hasBeach = TRUE THEN beach-ok = YES
(defrule abstraction::beach-ok
    (object (is-a Demand) (needBeach TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (beach-ok nil))
    (object (name ?dest) (hasBeach TRUE))
    =>
    (send ?of put-beach-ok YES)
)

; IF needBeach = TRUE AND hasBeach = FALSE THEN beach-ok = NO
(defrule abstraction::beach-no
    (object (is-a Demand) (needBeach TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (beach-ok nil))
    (object (name ?dest) (hasBeach FALSE))
    =>
    (send ?of put-beach-ok NO)
)

;; Mountain
; IF needMountain = FALSE THEN mountain-ok = YES
(defrule abstraction::mountain-not-needed
    (object (is-a Demand) (needMountain FALSE))
    ?of <- (object (is-a Offer) (mountain-ok nil))
    =>
    (send ?of put-mountain-ok YES)
)

; IF needMountain = TRUE AND hasMountain = TRUE THEN mountain-ok = YES
(defrule abstraction::mountain-ok
    (object (is-a Demand) (needMountain TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (mountain-ok nil))
    (object (name ?dest) (hasMountain TRUE))
    =>
    (send ?of put-mountain-ok YES)
)

; IF needMountain = TRUE AND hasMountain = FALSE THEN mountain-ok = NO
(defrule abstraction::mountain-no
    (object (is-a Demand) (needMountain TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (mountain-ok nil))
    (object (name ?dest) (hasMountain FALSE))
    =>
    (send ?of put-mountain-ok NO)
)

;; Culture
; IF needCulture = FALSE THEN culture-ok = YES
(defrule abstraction::culture-not-needed
    (object (is-a Demand) (needCulture FALSE))
    ?of <- (object (is-a Offer) (culture-ok nil))
    =>
    (send ?of put-culture-ok YES)
)

; IF needCulture = TRUE AND hasCulture = TRUE THEN culture-ok = YES
(defrule abstraction::culture-ok
    (object (is-a Demand) (needCulture TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (culture-ok nil))
    (object (name ?dest) (hasCulture TRUE))
    =>
    (send ?of put-culture-ok YES)
)

; IF needCulture = TRUE AND hasCulture = FALSE THEN culture-ok = NO
(defrule abstraction::culture-no
    (object (is-a Demand) (needCulture TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (culture-ok nil))
    (object (name ?dest) (hasCulture FALSE))
    =>
    (send ?of put-culture-ok NO)
)

;; Party
; IF needParty = FALSE THEN party-ok = YES
(defrule abstraction::party-not-needed
    (object (is-a Demand) (needParty FALSE))
    ?of <- (object (is-a Offer) (party-ok nil))
    =>
    (send ?of put-party-ok YES)
)

; IF needParty = TRUE AND hasParty = TRUE THEN party-ok = YES
(defrule abstraction::party-ok
    (object (is-a Demand) (needParty TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (party-ok nil))
    (object (name ?dest) (hasParty TRUE))
    =>
    (send ?of put-party-ok YES)
)

; IF needParty = TRUE AND hasParty = FALSE THEN party-ok = NO
(defrule abstraction::party-no
    (object (is-a Demand) (needParty TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (party-ok nil))
    (object (name ?dest) (hasParty FALSE))
    =>
    (send ?of put-party-ok NO)
)

;; Activities
; IF needActivities = FALSE THEN activities-ok = YES
(defrule abstraction::activities-not-needed
    (object (is-a Demand) (needActivities FALSE))
    ?of <- (object (is-a Offer) (activities-ok nil))
    =>
    (send ?of put-activities-ok YES)
)

; IF needActivities = TRUE AND hasActivities = TRUE THEN activities-ok = YES
(defrule abstraction::activities-ok
    (object (is-a Demand) (needActivities TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (activities-ok nil))
    (object (name ?dest) (hasActivities TRUE))
    =>
    (send ?of put-activities-ok YES)
)

; IF needActivities = TRUE AND hasActivities = FALSE THEN activities-ok = NO
(defrule abstraction::activities-no
    (object (is-a Demand) (needActivities TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (activities-ok nil))
    (object (name ?dest) (hasActivities FALSE))
    =>
    (send ?of put-activities-ok NO)
)

;; History
; IF needHistory = FALSE THEN history-ok = YES
(defrule abstraction::history-not-needed
    (object (is-a Demand) (needHistory FALSE))
    ?of <- (object (is-a Offer) (history-ok nil))
    =>
    (send ?of put-history-ok YES)
)

; IF needHistory = TRUE AND hasHistory = TRUE THEN history-ok = YES
(defrule abstraction::history-ok
    (object (is-a Demand) (needHistory TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (history-ok nil))
    (object (name ?dest) (hasHistory TRUE))
    =>
    (send ?of put-history-ok YES)
)

; IF needHistory = TRUE AND hasHistory = FALSE THEN history-ok = NO
(defrule abstraction::history-no
    (object (is-a Demand) (needHistory TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (history-ok nil))
    (object (name ?dest) (hasHistory FALSE))
    =>
    (send ?of put-history-ok NO)
)

;; Nature
; IF needNature = FALSE THEN nature-ok = YES
(defrule abstraction::nature-not-needed
    (object (is-a Demand) (needNature FALSE))
    ?of <- (object (is-a Offer) (nature-ok nil))
    =>
    (send ?of put-nature-ok YES)
)

; IF needNature = TRUE AND hasNature = TRUE THEN nature-ok = YES
(defrule abstraction::nature-ok
    (object (is-a Demand) (needNature TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (nature-ok nil))
    (object (name ?dest) (hasNature TRUE))
    =>
    (send ?of put-nature-ok YES)
)

; IF needNature = TRUE AND hasNature = FALSE THEN nature-ok = NO
(defrule abstraction::nature-no
    (object (is-a Demand) (needNature TRUE))
    ?of <- (object (is-a Offer) (Destination ?dest) (nature-ok nil))
    (object (name ?dest) (hasNature FALSE))
    =>
    (send ?of put-nature-ok NO)
)

; Compute geographic distance from user origin to each destination.
(defrule abstraction::compute-origin-distance
    (object (is-a Demand) (originLatitude ?olat) (originLongitude ?olon))
    ?of <- (object (is-a Offer) (Destination ?dest))
    (object (name ?dest) (location ?loc))
    (object (name ?loc) (latitude ?dlat) (longitude ?dlon))
    =>
    (send ?of put-distanceFromOrigin (distance-km ?olat ?olon ?dlat ?dlon))
)

; Strict month filter if no flexibility: only exact month.
(defrule abstraction::filter-month-no-flexibility
    (object (is-a Demand) (month ?m) (flexibility NONE))
    ?of <- (object (is-a Offer) (month ?om&:(<> ?om ?m)) (Destination ?dest&~[nil]))
    =>
    (send ?of put-Destination [nil])
)

; Flexible month filter: allow at most +/- 1 month.
(defrule abstraction::filter-month-with-flexibility
    (object (is-a Demand) (month ?m) (flexibility ?f&:(or (eq ?f LOW) (eq ?f HIGH))))
    ?of <- (object (is-a Offer) (month ?om) (Destination ?dest&~[nil]))
    (test (> (month-distance ?m ?om) 1))
    =>
    (send ?of put-Destination [nil])
)

(defrule abstraction::next-step
    (declare (salience -100))
    =>
    (focus heuristic))