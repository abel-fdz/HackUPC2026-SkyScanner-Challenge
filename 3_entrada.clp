;;; Input module: collects user preferences to recommend travel destinations

(defmodule input
    (import MAIN ?ALL)
    (export ?ALL)
)

;;; Template to control the input flow
(deftemplate input::input-phase
    (slot phase (type SYMBOL))
)

(deftemplate input::input-completed
    (slot completed (type SYMBOL) (default TRUE))
)

;;; -------------------------------------------------------
;;; Input rules
;;; -------------------------------------------------------

(defrule input::show-welcome
    (declare (salience 100))
    (not (input-phase))
    (not (input-completed))
    =>
    (printout t crlf "=== TRAVEL DESTINATION RECOMMENDATION SYSTEM ===" crlf crlf)
    (make-instance [demand] of Demand)
    (assert (input-phase (phase BUDGET)))
)

;;; --- BUDGET ---

(defrule input::ask-budget
    ?f <- (input-phase (phase BUDGET))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t "-- BUDGET --" crlf)
    (printout t "Maximum total budget (€): ")
    (bind ?resp (readline))
    (bind ?budget (string-to-field ?resp))
    (send ?d put-budgetMax (float ?budget))
    (modify ?f (phase DATE))
)

;;; --- DATE AND DURATION ---

(defrule input::ask-date
    ?f <- (input-phase (phase DATE))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- DATE AND DURATION --" crlf)
    (printout t "Travel month (1-12): ")
    (bind ?resp (readline))
    (bind ?month (string-to-field ?resp))
    (printout t "Trip duration (days): ")
    (bind ?resp (readline))
    (bind ?duration (string-to-field ?resp))
    (printout t "Date flexibility? (1.None 2.A few days 3.Weeks) [1]: ")
    (bind ?resp (readline))
    (bind ?opFlex (if (eq ?resp "") then 1 else (string-to-field ?resp)))
    (bind ?flex (switch ?opFlex
        (case 2 then LOW)
        (case 3 then HIGH)
        (default NONE)
    ))
    (send ?d put-month (integer ?month))
    (send ?d put-tripDuration (integer ?duration))
    (send ?d put-flexibility ?flex)
    (modify ?f (phase ORIGIN))
)

;;; --- ORIGIN, CONTINENT AND DISTANCE PREFERENCE ---

(defrule input::ask-origin
    ?f <- (input-phase (phase ORIGIN))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- ORIGIN AND DISTANCE PREFERENCE --" crlf)
    (printout t "Origin latitude (e.g., 41.38): ")
    (bind ?resp (readline))
    (bind ?lat (string-to-field ?resp))
    (printout t "Origin longitude (e.g., 2.17): ")
    (bind ?resp (readline))
    (bind ?lon (string-to-field ?resp))
    (printout t "Preferred continent (1.Europe 2.Asia 3.Africa 4.North America 5.South America 6.Oceania 7.Any) [7]: ")
    (bind ?resp (readline))
    (bind ?opCont (if (eq ?resp "") then 7 else (string-to-field ?resp)))
    (bind ?cont (switch ?opCont
        (case 1 then "Europe")
        (case 2 then "Asia")
        (case 3 then "Africa")
        (case 4 then "North America")
        (case 5 then "South America")
        (case 6 then "Oceania")
        (default "ANY")
    ))
    (printout t "Distance preference (1.NEAR 2.FAR 3.ANY) [3]: ")
    (bind ?resp (readline))
    (bind ?opProx (if (eq ?resp "") then 3 else (string-to-field ?resp)))
    (bind ?prox (switch ?opProx
        (case 1 then NEAR)
        (case 2 then FAR)
        (default ANY)
    ))
    (send ?d put-originLatitude (float ?lat))
    (send ?d put-originLongitude (float ?lon))
    (send ?d put-preferredContinent ?cont)
    (send ?d put-proximityPreference ?prox)
    (modify ?f (phase TRIP_TYPE))
)

;;; --- TRIP TYPE ---

(defrule input::ask-trip-type
    ?f <- (input-phase (phase TRIP_TYPE))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- TRIP TYPE --" crlf)
    (printout t "Trip type (1.ADVENTURE 2.RELAXATION 3.CULTURAL 4.ROMANTIC 5.FAMILY 6.BUSINESS) [1]: ")
    (bind ?resp (readline))
    (bind ?opType (if (eq ?resp "") then 1 else (string-to-field ?resp)))
    (bind ?type (switch ?opType
        (case 1 then ADVENTURE)
        (case 2 then RELAXATION)
        (case 3 then CULTURAL)
        (case 4 then ROMANTIC)
        (case 5 then FAMILY)
        (case 6 then BUSINESS)
        (default ADVENTURE)
    ))
    (send ?d put-tripType ?type)
    (modify ?f (phase CLIMATE))
)

;;; --- CLIMATE AND TEMPERATURE ---

(defrule input::ask-climate
    ?f <- (input-phase (phase CLIMATE))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- CLIMATE AND TEMPERATURE --" crlf)
    (printout t "Preferred climate (1.DRY 2.HUMID 3.TROPICAL 4.TEMPERATE 5.COLD 6.ANY) [6]: ")
    (bind ?resp (readline))
    (bind ?opClimate (if (eq ?resp "") then 6 else (string-to-field ?resp)))
    (bind ?climate (switch ?opClimate
        (case 1 then DRY)
        (case 2 then HUMID)
        (case 3 then TROPICAL)
        (case 4 then TEMPERATE)
        (case 5 then COLD)
        (default ANY)
    ))
    (printout t "Preferred temperature (1.HOT 2.MILD 3.COLD 4.ANY) [4]: ")
    (bind ?resp (readline))
    (bind ?opTemp (if (eq ?resp "") then 4 else (string-to-field ?resp)))
    (bind ?temp (switch ?opTemp
        (case 1 then HOT)
        (case 2 then MILD)
        (case 3 then COLD)
        (default ANY)
    ))
    (send ?d put-climate ?climate)
    (send ?d put-temperature ?temp)
    (modify ?f (phase NATURE))
)

;;; --- NATURAL ENVIRONMENT ---

(defrule input::ask-nature
    ?f <- (input-phase (phase NATURE))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- NATURAL ENVIRONMENT --" crlf)
    (printout t "Do you need a beach? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?beach (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (printout t "Do you need mountains? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?mountain (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (printout t "Do you need nature/green spaces? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?nature (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (send ?d put-needBeach ?beach)
    (send ?d put-needMountain ?mountain)
    (send ?d put-needNature ?nature)
    (modify ?f (phase POPULATION))
)

;;; --- POPULATION TYPE ---

(defrule input::ask-population
    ?f <- (input-phase (phase POPULATION))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- DESTINATION TYPE --" crlf)
    (printout t "Preferred population type (1.MAJOR-CITY 2.CITY 3.RURAL 4.ANY) [4]: ")
    (bind ?resp (readline))
    (bind ?opPop (if (eq ?resp "") then 4 else (string-to-field ?resp)))
    (bind ?pop (switch ?opPop
        (case 1 then MAJOR-CITY)
        (case 2 then CITY)
        (case 3 then RURAL)
        (default ANY)
    ))
    (send ?d put-typePopulation ?pop)
    (modify ?f (phase ACTIVITIES))
)

;;; --- ACTIVITIES AND INTERESTS ---

(defrule input::ask-activities
    ?f <- (input-phase (phase ACTIVITIES))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- ACTIVITIES AND INTERESTS --" crlf)
    (printout t "Are you interested in culture/museums/art? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?culture (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (printout t "Are you interested in nightlife/parties? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?party (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (printout t "Are you interested in adventure/sports activities? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?activities (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (printout t "Are you interested in historical sites/heritage? (y/n) [n]: ")
    (bind ?resp (readline))
    (bind ?history (if (member$ ?resp (create$ "y" "Y" "yes" "YES")) then TRUE else FALSE))
    (send ?d put-needCulture ?culture)
    (send ?d put-needParty ?party)
    (send ?d put-needActivities ?activities)
    (send ?d put-needHistory ?history)
    (modify ?f (phase END))
)

;;; --- OFFERS ---

(defrule input::ask-offers
    ?f <- (input-phase (phase END))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf "-- OFFERS FILTERS --" crlf)
    (printout t "Would you like to filter offers? (y/n) [n]: ")
    (bind ?resp (readline))
    (if (member$ ?resp (create$ "y" "Y" "yes" "YES"))
        then
            (make-instance [offers-filter] of Offer)
            (printout t "Maximum offer price (€) [any]: ")
            (bind ?price (readline))
            (if (neq ?price "")
                then
                    (send [offers-filter] put-price (integer (string-to-field ?price)))
            )
            (printout t "Offer duration (days) [any]: ")
            (bind ?duration (readline))
            (if (neq ?duration "")
                then
                    (send [offers-filter] put-duration (integer (string-to-field ?duration)))
            )
            (printout t "Offers filter created." crlf)
        else
            (printout t "Skipping offers filtering." crlf)
    )
    (modify ?f (phase END_SUMMARY))
)

;;; --- SUMMARY AND COMPLETION ---

(defrule input::finalize
    ?f <- (input-phase (phase END_SUMMARY))
    ?d <- (object (is-a Demand) (name [demand]))
    =>
    (printout t crlf crlf "=== SEARCH SUMMARY ===" crlf)
    (printout t "Maximum budget: " (send ?d get-budgetMax) "€" crlf)
    (printout t "Month: " (send ?d get-month) " | Duration: " (send ?d get-tripDuration) " days | Flexibility: " (send ?d get-flexibility) crlf)
    (printout t "Origin: (" (send ?d get-originLatitude) ", " (send ?d get-originLongitude) ")" crlf)
    (printout t "Preferred continent: " (send ?d get-preferredContinent) " | Distance preference: " (send ?d get-proximityPreference) crlf)
    (printout t "Trip type: " (send ?d get-tripType) crlf)
    (printout t "Climate: " (send ?d get-climate) " | Temperature: " (send ?d get-temperature) crlf)
    (printout t "Beach: " (send ?d get-needBeach) " | Mountain: " (send ?d get-needMountain) " | Nature: " (send ?d get-needNature) crlf)
    (printout t "Destination type: " (send ?d get-typePopulation) crlf)
    (printout t "Culture: " (send ?d get-needCulture) " | Party: " (send ?d get-needParty) " | Activities: " (send ?d get-needActivities) " | History: " (send ?d get-needHistory) crlf)
    (printout t crlf "Searching for destinations and offers..." crlf crlf)
    (retract ?f)
    (assert (input-completed))
    (focus abstraction)
)
