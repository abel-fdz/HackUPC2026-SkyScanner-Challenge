(definstances travel-data
    ;;; --- LOCATIONS ---
    ([loc-barcelona] of Location
        (latitude 41.3851) (longitude 2.1734)
        (continent "Europe") (country "Spain")
        (address "Placa de Catalunya") (district "Barcelona"))
    ([loc-lisbon] of Location
        (latitude 38.7223) (longitude -9.1393)
        (continent "Europe") (country "Portugal")
        (address "Praca do Comercio") (district "Lisbon"))
    ([loc-reykjavik] of Location
        (latitude 64.1466) (longitude -21.9426)
        (continent "Europe") (country "Iceland")
        (address "Laugavegur 1") (district "Midborg"))
    ([loc-marrakech] of Location
        (latitude 31.6295) (longitude -7.9811)
        (continent "Africa") (country "Morocco")
        (address "Jemaa el-Fnaa") (district "Medina"))
    ([loc-bangkok] of Location
        (latitude 13.7563) (longitude 100.5018)
        (continent "Asia") (country "Thailand")
        (address "Sukhumvit Road") (district "Khlong Toei"))
    ([loc-vancouver] of Location
        (latitude 49.2827) (longitude -123.1207)
        (continent "North America") (country "Canada")
        (address "Canada Place") (district "Downtown"))
    ([loc-cusco] of Location
        (latitude -13.5319) (longitude -71.9675)
        (continent "South America") (country "Peru")
        (address "Plaza de Armas") (district "Cusco Centro"))
    ([loc-queenstown] of Location
        (latitude -45.0312) (longitude 168.6626)
        (continent "Oceania") (country "New Zealand")
        (address "Shotover Street") (district "Queenstown"))

    ;;; --- DESTINATIONS ---
    ([dest-barcelona] of Destination
        (hasClimate TEMPERATE) (hasTemperature MILD)
        (hasBeach TRUE) (hasMountain TRUE)
        (hasTypePopulation MAJOR-CITY)
        (hasCulture TRUE) (hasParty TRUE) (hasActivities TRUE)
        (hasHistory TRUE) (hasNature TRUE)
        (location [loc-barcelona]))

    ([dest-lisbon] of Destination
        (hasClimate DRY) (hasTemperature MILD)
        (hasBeach TRUE) (hasMountain FALSE)
        (hasTypePopulation CITY)
        (hasCulture TRUE) (hasParty TRUE) (hasActivities TRUE)
        (hasHistory TRUE) (hasNature TRUE)
        (location [loc-lisbon]))

    ([dest-reykjavik] of Destination
        (hasClimate COLD) (hasTemperature COLD)
        (hasBeach FALSE) (hasMountain TRUE)
        (hasTypePopulation CITY)
        (hasCulture TRUE) (hasParty FALSE) (hasActivities TRUE)
        (hasHistory TRUE) (hasNature TRUE)
        (location [loc-reykjavik]))

    ([dest-marrakech] of Destination
        (hasClimate DRY) (hasTemperature HOT)
        (hasBeach FALSE) (hasMountain FALSE)
        (hasTypePopulation CITY)
        (hasCulture TRUE) (hasParty TRUE) (hasActivities TRUE)
        (hasHistory TRUE) (hasNature FALSE)
        (location [loc-marrakech]))

    ([dest-bangkok] of Destination
        (hasClimate HUMID) (hasTemperature HOT)
        (hasBeach FALSE) (hasMountain FALSE)
        (hasTypePopulation MAJOR-CITY)
        (hasCulture TRUE) (hasParty TRUE) (hasActivities TRUE)
        (hasHistory TRUE) (hasNature FALSE)
        (location [loc-bangkok]))

    ([dest-vancouver] of Destination
        (hasClimate TEMPERATE) (hasTemperature MILD)
        (hasBeach TRUE) (hasMountain TRUE)
        (hasTypePopulation CITY)
        (hasCulture TRUE) (hasParty FALSE) (hasActivities TRUE)
        (hasHistory FALSE) (hasNature TRUE)
        (location [loc-vancouver]))

    ([dest-cusco] of Destination
        (hasClimate DRY) (hasTemperature MILD)
        (hasBeach FALSE) (hasMountain TRUE)
        (hasTypePopulation RURAL)
        (hasCulture TRUE) (hasParty FALSE) (hasActivities TRUE)
        (hasHistory TRUE) (hasNature TRUE)
        (location [loc-cusco]))

    ([dest-queenstown] of Destination
        (hasClimate COLD) (hasTemperature COLD)
        (hasBeach TRUE) (hasMountain TRUE)
        (hasTypePopulation RURAL)
        (hasCulture FALSE) (hasParty TRUE) (hasActivities TRUE)
        (hasHistory FALSE) (hasNature TRUE)
        (location [loc-queenstown]))

    ;;; --- OFFERS ---
    ([offer1] of Offer
        (price 850) (duration 5) (Destination [dest-lisbon])
        (priceLevel LOW) (travelTime SHORT))
    ([offer2] of Offer
        (price 1200) (duration 7) (Destination [dest-barcelona])
        (priceLevel MEDIUM) (travelTime SHORT))
    ([offer3] of Offer
        (price 1650) (duration 8) (Destination [dest-marrakech])
        (priceLevel MEDIUM) (travelTime SHORT))
    ([offer4] of Offer
        (price 1900) (duration 10) (Destination [dest-vancouver])
        (priceLevel MEDIUM_HIGH) (travelTime LONG))
    ([offer5] of Offer
        (price 2300) (duration 12) (Destination [dest-bangkok])
        (priceLevel HIGH) (travelTime LONG))
    ([offer6] of Offer
        (price 2600) (duration 11) (Destination [dest-reykjavik])
        (priceLevel HIGH) (travelTime LONG))
    ([offer7] of Offer
        (price 1400) (duration 9) (Destination [dest-cusco])
        (priceLevel MEDIUM) (travelTime LONG))
    ([offer8] of Offer
        (price 3000) (duration 14) (Destination [dest-queenstown])
        (priceLevel HIGH) (travelTime LONG))
    ([offer9] of Offer
        (price 1100) (duration 6) (Destination [dest-lisbon])
        (priceLevel MEDIUM) (travelTime SHORT))
    ([offer10] of Offer
        (price 1750) (duration 8) (Destination [dest-barcelona])
        (priceLevel MEDIUM_HIGH) (travelTime SHORT))
    ([offer11] of Offer
        (price 950) (duration 5) (Destination [dest-marrakech])
        (priceLevel LOW) (travelTime SHORT))
    ([offer12] of Offer
        (price 2100) (duration 9) (Destination [dest-vancouver])
        (priceLevel HIGH) (travelTime LONG))
)
