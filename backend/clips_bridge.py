import json
from pathlib import Path


def _json_loads_loose(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def _to_bool_symbol(value) -> str:
    return "TRUE" if value is True else "FALSE"


def _map_symbol(value, mapping: dict, default: str) -> str:
    if value is None:
        return default
    key = str(value).strip().lower()
    return mapping.get(key, default)


def _build_demand_instance_cmd(data: dict) -> str:
    budget = float(data.get("maximum_total_budget_eur") or 3000)
    month = int(data.get("travel_month") or 7)
    duration = int(data.get("trip_duration_days") or 7)

    flexibility = _map_symbol(
        data.get("date_flexibility"),
        {"none": "NONE", "few_days": "LOW", "weeks": "HIGH"},
        "NONE",
    )
    trip_type = _map_symbol(
        data.get("trip_type"),
        {
            "adventure": "ADVENTURE",
            "relaxation": "RELAXATION",
            "cultural": "CULTURAL",
            "romantic": "ROMANTIC",
            "family": "FAMILY",
            "business": "BUSINESS",
        },
        "RELAXATION",
    )
    climate = _map_symbol(
        data.get("preferred_climate"),
        {
            "dry": "DRY",
            "humid": "HUMID",
            "tropical": "TROPICAL",
            "temperate": "TEMPERATE",
            "cold": "COLD",
            "any": "ANY",
        },
        "ANY",
    )
    temperature = _map_symbol(
        data.get("preferred_temperature"),
        {"hot": "HOT", "mild": "MILD", "cold": "COLD", "any": "ANY"},
        "ANY",
    )
    population = _map_symbol(
        data.get("preferred_population_type"),
        {"major_city": "MAJOR-CITY", "city": "CITY", "rural": "RURAL", "any": "ANY"},
        "ANY",
    )

    preferred_continent = _map_symbol(
        data.get("preferred_continent"),
        {
            "europe": "Europe",
            "asia": "Asia",
            "africa": "Africa",
            "north_america": "North America",
            "south_america": "South America",
            "oceania": "Oceania",
            "any": "ANY",
        },
        "ANY",
    )
    proximity = _map_symbol(
        data.get("proximity_preference"),
        {"near": "NEAR", "far": "FAR", "any": "ANY"},
        "ANY",
    )

    need_beach = _to_bool_symbol(data.get("needs_beach"))
    need_mountain = _to_bool_symbol(data.get("needs_mountains"))
    need_nature = _to_bool_symbol(data.get("needs_nature_green_spaces"))
    need_culture = _to_bool_symbol(data.get("interested_culture_museums_art"))
    need_party = _to_bool_symbol(data.get("interested_nightlife_parties"))
    need_activities = _to_bool_symbol(data.get("interested_adventure_sports"))
    need_history = _to_bool_symbol(data.get("interested_historical_sites_heritage"))

    # Default origin: Barcelona (unless JSON provides coordinates)
    origin_lat = float(data.get("origin_latitude") or 41.3874)
    origin_lon = float(data.get("origin_longitude") or 2.1686)

    return (
        "(make-instance [demand] of Demand "
        f"(budgetMax {budget}) "
        f"(month {month}) "
        f"(tripDuration {duration}) "
        f"(flexibility {flexibility}) "
        f"(tripType {trip_type}) "
        f"(climate {climate}) "
        f"(temperature {temperature}) "
        f"(originLatitude {origin_lat}) "
        f"(originLongitude {origin_lon}) "
        f'(preferredContinent "{preferred_continent}") '
        f"(proximityPreference {proximity}) "
        f"(needBeach {need_beach}) "
        f"(needMountain {need_mountain}) "
        f"(needNature {need_nature}) "
        f"(typePopulation {population}) "
        f"(needCulture {need_culture}) "
        f"(needParty {need_party}) "
        f"(needActivities {need_activities}) "
        f"(needHistory {need_history})"
        ")"
    )


def run_clips_from_preferences_json(preferences_json: str) -> str:
    """
    Runs CLIPS pipeline using AI-extracted JSON preferences.
    Returns CLIPS text output.
    """
    try:
        from clips import Environment, Router
    except Exception as exc:
        return f"CLIPS runtime not available. Install clipspy. Detail: {exc}"

    try:
        data = _json_loads_loose(preferences_json)
    except Exception as exc:
        return f"Invalid preferences JSON for CLIPS: {exc}"

    class CaptureRouter(Router):
        def __init__(self):
            super().__init__("capture-router", 20)
            self.buffer = []

        def query(self, logical_name):
            return logical_name in {"stdout", "stdwrn", "stderr"}

        def write(self, logical_name, message):
            self.buffer.append(message)

    root = Path(__file__).resolve().parent.parent
    clp_files = [
        "1_ontologia.clp",
        "2_instancias.clp",
        "3_entrada.clp",
        "4_abstraccion.clp",
        "5_heuristica.clp",
        "6_refinamiento.clp",
        "7_salida.clp",
    ]

    env = Environment()
    router = CaptureRouter()
    env.add_router(router)

    try:
        # In clipspy, a default MAIN module exists but may not export constructs.
        # Your CLP files import MAIN ?ALL, so we bootstrap MAIN as export ?ALL.
        try:
            env.build("(defmodule MAIN (export ?ALL))")
        except Exception:
            # If MAIN was already defined/exported by a previous load, continue.
            pass

        for filename in clp_files:
            env.load(str(root / filename))
        env.reset()
        env.eval(_build_demand_instance_cmd(data))
        env.eval("(focus abstraction heuristic refinement output)")
        env.run()
        output = "".join(router.buffer).strip()
        return output or "CLIPS completed with no textual output."
    except Exception as exc:
        return f"Error running CLIPS: {exc}"
