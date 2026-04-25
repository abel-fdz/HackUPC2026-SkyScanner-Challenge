(defclass Demand "Preferences and needs of the user searching a destination"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)
    ;;; Maximum budget of the user
    (slot budgetMax
        (type FLOAT)
        (create-accessor read-write))
    ;;; Date of the trip
    (slot month
        (type INTEGER)
        (create-accessor read-write))
    ;;; Trip Type
    (slot tripType
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Date felxibility
    (slot flexibility
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Preferred climate 
    (slot climate
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Preferred temperature
    (slot temperature
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Preferred trip duration (in days)
    (slot tripDuration
        (type INTEGER)
        (create-accessor read-write))

    ;;; Need of beaches: TRUE, FALSE
    (slot needBeach
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Need of mountains: TRUE, FALSE
    (slot needMountain
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Type of population: 
    (slot typePopulation
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Need of culture: TRUE, FALSE
    (slot needCulture
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Need of party: TRUE, FALSE
    (slot needParty
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Need of activities: TRUE, FALSE
    (slot needActivities
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Need of historic sites: TRUE, FALSE
    (slot needHistory
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Need of nature: TRUE, FALSE
    (slot needNature
        (type SYMBOL)
        (create-accessor read-write))

    (slot budgetLevel
        (type SYMBOL)
        (create-accessor read-write))

    (slot durationLevel
        (type SYMBOL)
        (create-accessor read-write))
)

(defclass Location "Geographical destination location"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)
    ;;; Latitude of the location
    (slot latitude
        (type FLOAT)
        (create-accessor read-write))
    ;;; Longitude of the location
    (slot longitude
        (type FLOAT)
        (create-accessor read-write))
    ;;; Destination continent
    (slot continent
        (type STRING)
        (create-accessor read-write))
    ;;; Destination country
    (slot country
        (type STRING)
        (create-accessor read-write))
    ;;; Address (optional)
    (slot address
        (type STRING)
        (create-accessor read-write))
    ;;; District/area (optional)
    (slot district
        (type STRING)
        (create-accessor read-write))
)

(defclass Destination "Destinations around the world"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)

    ;;; Preferred climate 
    (slot hasClimate
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Preferred temperature
    (slot hasTemperature
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has beaches: TRUE, FALSE
    (slot hasBeach
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has mountains: TRUE, FALSE
    (slot hasMountain
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Type of population: 
    (slot hasTypePopulation
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has culture: TRUE, FALSE
    (slot hasCulture
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has party life: TRUE, FALSE
    (slot hasParty
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has activities: TRUE, FALSE
    (slot hasActivities
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has historic sites: TRUE, FALSE
    (slot hasHistory
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Has nature: TRUE, FALSE
    (slot hasNature
        (type SYMBOL)
        (create-accessor read-write))
    ;;; Location of the destination
    (slot location
        (type INSTANCE)
        (create-accessor read-write))
)

(defclass Offer "Destination offers"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)

    (slot price
        (type INTEGER)
        (create-accessor read-write))
    (slot duration
        (type INTEGER)
        (create-accessor read-write))
    (slot Destination
        (type INSTANCE)
        (create-accessor read-write))

    ;;; Abstraction results - binary features
    (slot beach-ok      (type SYMBOL) (create-accessor read-write))
    (slot mountain-ok   (type SYMBOL) (create-accessor read-write))
    (slot culture-ok    (type SYMBOL) (create-accessor read-write))
    (slot party-ok      (type SYMBOL) (create-accessor read-write))
    (slot activities-ok (type SYMBOL) (create-accessor read-write))
    (slot history-ok    (type SYMBOL) (create-accessor read-write))
    (slot nature-ok     (type SYMBOL) (create-accessor read-write))

    ;;; Abstraction results - graded features
    (slot climate-ok     (type SYMBOL) (create-accessor read-write))
    (slot temperature-ok (type SYMBOL) (create-accessor read-write))
    (slot population-ok  (type SYMBOL) (create-accessor read-write))
    (slot duration-ok    (type SYMBOL) (create-accessor read-write))

    ;;; Heuristic slots
    (slot score      (type FLOAT)   (create-accessor read-write))
    (slot grade      (type SYMBOL)  (create-accessor read-write))
    (slot priceLevel (type SYMBOL)  (create-accessor read-write))
    (slot travelTime (type SYMBOL)  (create-accessor read-write))
    
    ;;; Advantages and disadvantages lists
    (multislot advantages (create-accessor read-write))
    (multislot disadvantages (create-accessor read-write))
    
    ;;; Reason for recommendation
    (slot reason (type STRING) (create-accessor read-write))
)

(defclass Servicio "Service available at location"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)
    (slot tipoServicio
        (type SYMBOL)
        (create-accessor read-write))
    (slot location
        (type INSTANCE)
        (create-accessor read-write))
)

(defclass Vivienda "Housing/accommodation"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)
    (slot nombre
        (type STRING)
        (create-accessor read-write))
    (slot tipo
        (type SYMBOL)
        (create-accessor read-write))
    (slot habitaciones
        (type INTEGER)
        (create-accessor read-write))
    (slot m2
        (type FLOAT)
        (create-accessor read-write))
    (slot amueblado
        (type SYMBOL)
        (create-accessor read-write))
    (slot localizacion
        (type INSTANCE)
        (create-accessor read-write))
)

(defclass Oferta "Offer for accommodation"
    (is-a USER)
    (role concrete)
    (pattern-match reactive)
    (slot idOferta
        (type STRING)
        (create-accessor read-write))
    (slot precio
        (type FLOAT)
        (create-accessor read-write))
    (slot vivienda
        (type INSTANCE)
        (create-accessor read-write))
)