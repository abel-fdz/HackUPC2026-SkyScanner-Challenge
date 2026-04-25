import json
import os
from datetime import date
from pathlib import Path

import requests


SKYSCANNER_FLIGHTS_BASE_URL = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search"
SKYSCANNER_HOTELS_BASE_URL = os.getenv(
    "SKYSCANNER_HOTELS_BASE_URL",
    "https://partners.api.skyscanner.net/apiservices/v3/hotels/live/search",
).strip()


DESTINATION_CATALOG = [
    {
        "slug": "barcelona",
        "city": "Barcelona",
        "iata": "BCN",
        "latitude": 41.3874,
        "longitude": 2.1686,
        "continent": "Europe",
        "country": "Spain",
        "has_climate": "TEMPERATE",
        "has_temperature": "MILD",
        "has_beach": True,
        "has_mountain": True,
        "has_type_population": "MAJOR-CITY",
        "has_culture": True,
        "has_party": True,
        "has_activities": True,
        "has_history": True,
        "has_nature": True,
        "fallback_hotel_night_eur": 120,
    },
    {
        "slug": "lisbon",
        "city": "Lisbon",
        "iata": "LIS",
        "latitude": 38.7223,
        "longitude": -9.1393,
        "continent": "Europe",
        "country": "Portugal",
        "has_climate": "TEMPERATE",
        "has_temperature": "MILD",
        "has_beach": True,
        "has_mountain": False,
        "has_type_population": "CITY",
        "has_culture": True,
        "has_party": True,
        "has_activities": True,
        "has_history": True,
        "has_nature": True,
        "fallback_hotel_night_eur": 95,
    },
    {
        "slug": "rome",
        "city": "Rome",
        "iata": "FCO",
        "latitude": 41.9028,
        "longitude": 12.4964,
        "continent": "Europe",
        "country": "Italy",
        "has_climate": "TEMPERATE",
        "has_temperature": "HOT",
        "has_beach": False,
        "has_mountain": False,
        "has_type_population": "MAJOR-CITY",
        "has_culture": True,
        "has_party": True,
        "has_activities": True,
        "has_history": True,
        "has_nature": False,
        "fallback_hotel_night_eur": 110,
    },
    {
        "slug": "tokyo",
        "city": "Tokyo",
        "iata": "NRT",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "continent": "Asia",
        "country": "Japan",
        "has_climate": "TEMPERATE",
        "has_temperature": "MILD",
        "has_beach": False,
        "has_mountain": False,
        "has_type_population": "MAJOR-CITY",
        "has_culture": True,
        "has_party": True,
        "has_activities": True,
        "has_history": True,
        "has_nature": False,
        "fallback_hotel_night_eur": 140,
    },
    {
        "slug": "bangkok",
        "city": "Bangkok",
        "iata": "BKK",
        "latitude": 13.7563,
        "longitude": 100.5018,
        "continent": "Asia",
        "country": "Thailand",
        "has_climate": "TROPICAL",
        "has_temperature": "HOT",
        "has_beach": False,
        "has_mountain": False,
        "has_type_population": "MAJOR-CITY",
        "has_culture": True,
        "has_party": True,
        "has_activities": True,
        "has_history": True,
        "has_nature": False,
        "fallback_hotel_night_eur": 70,
    },
]


def _to_clips_bool(value: bool) -> str:
    return "TRUE" if bool(value) else "FALSE"


def _price_level(total_price: float) -> str:
    if total_price < 1200:
        return "LOW"
    if total_price < 2200:
        return "MEDIUM"
    return "HIGH"


def _safe_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _build_travel_date(month: int) -> date:
    m = month if 1 <= month <= 12 else date.today().month
    year = date.today().year
    if m < date.today().month:
        year += 1
    return date(year, m, 15)


def _fetch_skyscanner_flight(origin_iata: str, dest_iata: str, travel_date: date):
    api_key = os.getenv("SKYSCANNER_API_KEY", "").strip()
    if not api_key:
        return None

    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "query": {
            "market": "ES",
            "locale": "es-ES",
            "currency": "EUR",
            "queryLegs": [
                {
                    "originPlaceId": {"iata": origin_iata},
                    "destinationPlaceId": {"iata": dest_iata},
                    "date": {
                        "year": travel_date.year,
                        "month": travel_date.month,
                        "day": travel_date.day,
                    },
                }
            ],
            "adults": 1,
            "cabinClass": "CABIN_CLASS_ECONOMY",
        }
    }

    try:
        r = requests.post(f"{SKYSCANNER_FLIGHTS_BASE_URL}/create", json=payload, headers=headers, timeout=20)
        if r.status_code != 200:
            return None
        session_token = r.json().get("sessionToken")
        if not session_token:
            return None
        r2 = requests.post(f"{SKYSCANNER_FLIGHTS_BASE_URL}/poll/{session_token}", headers=headers, timeout=20)
        if r2.status_code != 200:
            return None
        data = r2.json()
        stats = data.get("content", {}).get("stats", {}).get("itineraries", {}).get("total", {})
        min_price_amount = stats.get("minPrice", {}).get("amount")
        if not min_price_amount:
            return None
        min_price_eur = float(min_price_amount) / 1000.0
        return {"flight_price": min_price_eur, "travel_time_h": 2.0}
    except Exception:
        return None


def _fetch_skyscanner_hotel_night(dest_iata: str, checkin_date: date, nights: int) -> float | None:
    api_key = os.getenv("SKYSCANNER_API_KEY", "").strip()
    if not api_key:
        return None
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    checkout_date = date(checkin_date.year, checkin_date.month, checkin_date.day).toordinal() + max(1, nights)
    checkout = date.fromordinal(checkout_date)
    payload = {
        "query": {
            "market": "ES",
            "locale": "es-ES",
            "currency": "EUR",
            "entityId": {"iata": dest_iata},
            "checkinDate": {
                "year": checkin_date.year,
                "month": checkin_date.month,
                "day": checkin_date.day,
            },
            "checkoutDate": {
                "year": checkout.year,
                "month": checkout.month,
                "day": checkout.day,
            },
            "rooms": 1,
            "adults": 2,
        }
    }
    try:
        r = requests.post(f"{SKYSCANNER_HOTELS_BASE_URL}/create", json=payload, headers=headers, timeout=20)
        if r.status_code != 200:
            return None
        session_token = r.json().get("sessionToken")
        if not session_token:
            return None
        r2 = requests.post(f"{SKYSCANNER_HOTELS_BASE_URL}/poll/{session_token}", headers=headers, timeout=20)
        if r2.status_code != 200:
            return None
        data = r2.json()
        # Intentamos varias rutas habituales de precio mínimo por noche
        amount = (
            data.get("content", {})
            .get("results", {})
            .get("stats", {})
            .get("minPrice", {})
            .get("amount")
        )
        if not amount:
            amount = (
                data.get("content", {})
                .get("stats", {})
                .get("hotels", {})
                .get("total", {})
                .get("minPrice", {})
                .get("amount")
            )
        if not amount:
            return None
        return float(amount) / 1000.0
    except Exception:
        return None


def _estimate_living_cost_from_skyscanner(hotel_night_eur: float) -> float:
    """
    Proxy de coste de vida basado en pricing de alojamiento (sin API externa).
    Lo mantenemos bajo datos de Skyscanner.
    """
    return max(20.0, hotel_night_eur * 0.45)


def generate_instances_clp(preferences: dict, output_path: str | Path) -> str:
    """
    Genera 2_instancias.clp dinámicamente:
    price = flight_avg + hotel_total + living_cost_proxy_total
    """
    origin_iata = os.getenv("DEFAULT_ORIGIN_IATA", "BCN").strip() or "BCN"
    duration_days = max(1, _safe_int(preferences.get("trip_duration_days"), 7))
    travel_month = _safe_int(preferences.get("travel_month"), date.today().month)
    max_budget = preferences.get("maximum_total_budget_eur")
    max_budget = None if max_budget is None else float(max_budget)
    travel_date = _build_travel_date(travel_month)

    loc_blocks = []
    dest_blocks = []
    offer_blocks = []

    included_idx = 0
    for d in DESTINATION_CATALOG:
        flight_data = _fetch_skyscanner_flight(origin_iata, d["iata"], travel_date) or {}
        flight_price = float(flight_data.get("flight_price", 850.0))
        travel_time_h = float(flight_data.get("travel_time_h", 2.0))

        hotel_night = _fetch_skyscanner_hotel_night(d["iata"], travel_date, duration_days)
        if hotel_night is None:
            hotel_night = float(d["fallback_hotel_night_eur"])
        living_day_proxy = _estimate_living_cost_from_skyscanner(hotel_night)

        hotel_total = hotel_night * duration_days
        living_total = living_day_proxy * duration_days
        total_price = flight_price + hotel_total + living_total

        if max_budget is not None and total_price > max_budget * 1.25:
            continue

        included_idx += 1
        slug = d["slug"]
        loc_name = f"loc-{slug}"
        dest_name = f"dest-{slug}"
        offer_name = f"offer-{slug}"

        loc_blocks.append(
            f"""    ([{loc_name}] of Location
        (latitude {d["latitude"]})
        (longitude {d["longitude"]})
        (continent "{d["continent"]}")
        (country "{d["country"]}"))"""
        )
        dest_blocks.append(
            f"""    ([{dest_name}] of Destination
        (hasClimate {d["has_climate"]})
        (hasTemperature {d["has_temperature"]})
        (hasBeach {_to_clips_bool(d["has_beach"])})
        (hasMountain {_to_clips_bool(d["has_mountain"])})
        (hasTypePopulation {d["has_type_population"]})
        (hasCulture {_to_clips_bool(d["has_culture"])})
        (hasParty {_to_clips_bool(d["has_party"])})
        (hasActivities {_to_clips_bool(d["has_activities"])})
        (hasHistory {_to_clips_bool(d["has_history"])})
        (hasNature {_to_clips_bool(d["has_nature"])})
        (location [{loc_name}]))"""
        )
        offer_blocks.append(
            f"""    ([{offer_name}] of Offer
        (price {_safe_int(round(total_price), 0)})
        (duration {duration_days})
        (Destination [{dest_name}])
        (priceLevel {_price_level(total_price)})
        (travelTime {round(travel_time_h, 1)})
        (score 0.0)
        (grade nil))"""
        )

        if included_idx >= 15:
            break

    all_blocks = []
    for i in range(len(loc_blocks)):
        all_blocks.extend([loc_blocks[i], dest_blocks[i], offer_blocks[i], ""])

    text = "(definstances instancies-generades\n" + "\n".join(all_blocks).rstrip() + "\n)\n"
    output = Path(output_path)
    output.write_text(text, encoding="utf-8")
    return str(output)


def parse_preferences_json(raw_json: str) -> dict:
    return json.loads(raw_json)
