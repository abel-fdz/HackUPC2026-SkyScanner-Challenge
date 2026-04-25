; ============================================
; OUTPUT MODULE - DESTINATION RECOMMENDER
; ============================================

(defmodule output
    (import MAIN ?ALL)
    (import refinement ?ALL)
    (export ?ALL)
)

; ============================================
; AUX FUNCTIONS
; ============================================

; Translate grade to readable text
(deffunction output::translate-grade (?g)
    (switch ?g
        (case VERY_RECOMMENDED then "*** VERY RECOMMENDED ***")
        (case RECOMMENDED then "** RECOMMENDED **")
        (case PARTIAL then "* PARTIAL MATCH *")
        (case NOT_SUITABLE then "NOT SUITABLE")
        (default ""))
)

; Format list with commas
(deffunction output::format-list (?list)
    (if (= (length$ ?list) 0)
        then "-"
        else
        (bind ?res (nth$ 1 ?list))
        (loop-for-count (?i 2 (length$ ?list))
            (bind ?res (str-cat ?res ", " (nth$ ?i ?list))))
        ?res)
)

; Convert numeric month to short label.
(deffunction output::month-label (?m)
    (switch ?m
        (case 1 then "JAN")
        (case 2 then "FEB")
        (case 3 then "MAR")
        (case 4 then "APR")
        (case 5 then "MAY")
        (case 6 then "JUN")
        (case 7 then "JUL")
        (case 8 then "AUG")
        (case 9 then "SEP")
        (case 10 then "OCT")
        (case 11 then "NOV")
        (case 12 then "DEC")
        (default "?"))
)

; Simple tags for destination features
(deffunction output::destination-tags (?of)
    (bind ?txt "")
    (bind ?dest (send ?of get-Destination))
    (if (eq ?dest [nil]) then (return "-"))
    
    (if (eq (send ?dest get-hasBeach) TRUE)
        then (bind ?txt (str-cat ?txt "Beach ")))
        
    (if (eq (send ?dest get-hasCulture) TRUE)
        then (bind ?txt (str-cat ?txt "Culture ")))
        
    (if (eq (send ?dest get-hasNature) TRUE)
        then (bind ?txt (str-cat ?txt "Nature ")))
        
    (if (eq (str-length ?txt) 0)
        then "-"
        else (sub-string 1 (- (str-length ?txt) 1) ?txt))
)

; ============================================
; OUTPUT RULES
; ============================================

; Header
(defrule output::header
    (declare (salience 100))
    (summary (total ?t&:(> ?t 0)))
    =>
    (printout t crlf)
    (printout t "============================================================" crlf)
    (printout t "                TOP 5 DESTINATION RECOMMENDATIONS           " crlf)
    (printout t "============================================================" crlf)
)

; Summary
(defrule output::show-summary
    (declare (salience 99))
    (summary (total ?t) 
             (very-recommended ?vr) 
             (recommended ?r) 
             (partial ?p) 
             (not-suitable ?ns))
    (test (> ?t 0))
    =>
    (printout t "Total: " ?t " destinations (" 
              ?vr " very recommended, "
              ?r " recommended, "
              ?p " partial)" crlf)
    (printout t "------------------------------------------------------------" crlf)
)

; Print selected offers in order
(defrule output::print-offer
    (declare (salience 90))
    (selection (position ?pos) (offer ?of) (original-grade ?g))
    (test (neq (send ?of get-Destination) [nil]))
    (not (printed ?pos))
    (not (and (selection (position ?p2))
              (test (< ?p2 ?pos))
              (not (printed ?p2))))
    =>
    (bind ?dest (send ?of get-Destination))
    (bind ?label "Unknown destination")
    (if (neq ?dest [nil])
        then
        (bind ?loc (send ?dest get-location))
        (bind ?label (send ?loc get-country)))
    (bind ?price (send ?of get-price))
    (bind ?month (send ?of get-month))
    (bind ?score (send ?of get-score))
    (bind ?advantages (send ?of get-advantages))
    (bind ?disadvantages (send ?of get-disadvantages))
    (bind ?reason (send ?of get-reason))

    (printout t crlf ?pos ". " ?label " (" (month-label ?month) ") " (translate-grade ?g) crlf)
    (printout t "   Price: " ?price "€ | Score: " ?score crlf)
    (printout t "   Type: " (destination-tags ?of) crlf)
    (printout t "   Travel time: " (send ?of get-travelTime) crlf)
    (printout t "   Distance from origin: " (integer (send ?of get-distanceFromOrigin)) " km" crlf)

    (printout t "   [+] Advantages: " (format-list ?advantages) crlf)
    (printout t "   [-] Disadvantages: " (format-list ?disadvantages) crlf)

    (printout t "   -> Reason: " ?reason crlf)

    (assert (printed ?pos))
)

; Footer
(defrule output::footer
    (declare (salience -5))
    (summary (total ?t&:(> ?t 0)))
    =>
    (printout t crlf "============================================================" crlf crlf)
)

; No results
(defrule output::no-results
    (declare (salience -10))
    (summary (total 0))
    =>
    (printout t crlf "============================================================" crlf)
    (printout t "                   NO DESTINATIONS FOUND                    " crlf)
    (printout t "============================================================" crlf crlf)
)