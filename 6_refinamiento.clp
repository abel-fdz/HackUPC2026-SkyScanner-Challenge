; ============================================
; REFINEMENT MODULE - TOP DESTINATIONS
; ============================================

(defmodule refinement
    (import MAIN ?ALL)
    (export ?ALL)
)

; ============================================
; TEMPLATES
; ============================================

(deftemplate refinement::selection
    (slot position (type INTEGER))
    (slot offer (type INSTANCE))
    (slot original-grade (type SYMBOL))
)

(deftemplate refinement::counter
    (slot value (type INTEGER) (default 0))
)

(deftemplate refinement::summary
    (slot total (type INTEGER) (default 0))
    (slot very-recommended (type INTEGER) (default 0))
    (slot recommended (type INTEGER) (default 0))
    (slot partial (type INTEGER) (default 0))
    (slot not-suitable (type INTEGER) (default 0))
)

; ============================================
; AUX FUNCTION
; ============================================

(deffunction refinement::get-score (?of)
    (return (send ?of get-score))
)

; ============================================
; INITIALIZATION
; ============================================

(defrule refinement::initialize
    (declare (salience 10))
    (not (counter))
    =>
    (assert (counter (value 0)))

    (bind ?vr (length$ (find-all-instances ((?o Offer)) (eq ?o:grade VERY_RECOMMENDED))))
    (bind ?r  (length$ (find-all-instances ((?o Offer)) (eq ?o:grade RECOMMENDED))))
    (bind ?p  (length$ (find-all-instances ((?o Offer)) (eq ?o:grade PARTIAL))))
    (bind ?ns (length$ (find-all-instances ((?o Offer)) (eq ?o:grade NOT_SUITABLE))))
    (bind ?total (+ ?vr ?r ?p ?ns))

    (assert (summary
        (total ?total)
        (very-recommended ?vr)
        (recommended ?r)
        (partial ?p)
        (not-suitable ?ns)))
)

; ============================================
; TOP 5 SELECTION
; ============================================

; VERY RECOMMENDED (highest priority)
(defrule refinement::select-very-recommended
    (declare (salience 4))
    ?c <- (counter (value ?n&:(< ?n 5)))
    ?of <- (object (is-a Offer) (grade VERY_RECOMMENDED))
    (not (object (is-a Offer) (grade VERY_RECOMMENDED)
        (name ?other&:(and (neq ?other (instance-name ?of))
                           (> (get-score (instance-address * ?other))
                              (get-score ?of))))))
    =>
    (assert (selection (position (+ ?n 1)) (offer ?of) (original-grade VERY_RECOMMENDED)))
    (modify ?c (value (+ ?n 1)))
    (send ?of put-grade SELECTED)
)

; RECOMMENDED
(defrule refinement::select-recommended
    (declare (salience 3))
    ?c <- (counter (value ?n&:(< ?n 5)))
    ?of <- (object (is-a Offer) (grade RECOMMENDED))
    (not (object (is-a Offer) (grade RECOMMENDED)
        (name ?other&:(and (neq ?other (instance-name ?of))
                           (> (get-score (instance-address * ?other))
                              (get-score ?of))))))
    =>
    (assert (selection (position (+ ?n 1)) (offer ?of) (original-grade RECOMMENDED)))
    (modify ?c (value (+ ?n 1)))
    (send ?of put-grade SELECTED)
)

; PARTIAL
(defrule refinement::select-partial
    (declare (salience 2))
    ?c <- (counter (value ?n&:(< ?n 5)))
    ?of <- (object (is-a Offer) (grade PARTIAL))
    (not (object (is-a Offer) (grade PARTIAL)
        (name ?other&:(and (neq ?other (instance-name ?of))
                           (> (get-score (instance-address * ?other))
                              (get-score ?of))))))
    =>
    (assert (selection (position (+ ?n 1)) (offer ?of) (original-grade PARTIAL)))
    (modify ?c (value (+ ?n 1)))
    (send ?of put-grade SELECTED)
)

; NOT SUITABLE (fallback)
(defrule refinement::select-not-suitable
    (declare (salience 1))
    ?c <- (counter (value ?n&:(< ?n 5)))
    ?of <- (object (is-a Offer) (grade NOT_SUITABLE))
    (not (object (is-a Offer) (grade NOT_SUITABLE)
        (name ?other&:(and (neq ?other (instance-name ?of))
                           (> (get-score (instance-address * ?other))
                              (get-score ?of))))))
    =>
    (assert (selection (position (+ ?n 1)) (offer ?of) (original-grade NOT_SUITABLE)))
    (modify ?c (value (+ ?n 1)))
    (send ?of put-grade SELECTED)
)

; ============================================
; NEXT MODULE
; ============================================

(defrule refinement::next-step
    (declare (salience -10))
    =>
    (focus output)
)