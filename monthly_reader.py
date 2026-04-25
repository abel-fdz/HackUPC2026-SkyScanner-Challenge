import json
import unicodedata
from collections import defaultdict
from pathlib import Path

OUTPUT_CLIPS = "dataset.clp"

MONTH_NAMES = {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DEC",
}

# Accepts common Catalan/Spanish variants and typos found in files.
MONTH_FILE_ALIASES = {
    "gener": 1,
    "ene": 1,
    "january": 1,
    "febrer": 2,
    "feb": 2,
    "february": 2,
    "marc": 3,
    "març": 3,
    "març": 3,
    "març": 3,
    "marzo": 3,
    "abril": 4,
    "apr": 4,
    "maig": 5,
    "mayo": 5,
    "may": 5,
    "juny": 6,
    "jun": 6,
    "juliol": 7,
    "jul": 7,
    "agost": 8,
    "ago": 8,
    "aug": 8,
    "setembre": 9,
    "septembre": 9,
    "sep": 9,
    "octubre": 10,
    "oct": 10,
    "novembre": 11,
    "nov": 11,
    "desembre": 12,
    "decembre": 12,
    "dicembre": 12,
    "dec": 12,
}


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def safe_id(iata: str) -> str:
    return iata.lower()


def discover_month_files() -> tuple[list[Path], set[int]]:
    month_files: list[Path] = []
    months_from_names: set[int] = set()

    for path in sorted(Path(".").glob("*.txt")):
        stem_normalized = normalize_name(path.stem)
        if stem_normalized in MONTH_FILE_ALIASES:
            month_files.append(path)
            months_from_names.add(MONTH_FILE_ALIASES[stem_normalized])
    return month_files, months_from_names


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    month_files, months_from_names = discover_month_files()
    if not month_files:
        raise SystemExit("No s'han trobat fitxers mensuals .txt (ex: gener.txt, agost.txt, ...)")

    airport_info: dict[str, dict] = {}
    prices_by_dest_month: dict[str, dict[int, list[int]]] = defaultdict(lambda: defaultdict(list))

    for file_path in month_files:
        data = load_json(file_path)
        results = data.get("content", {}).get("results", {})
        quotes = results.get("quotes", {})
        places = results.get("places", {})

        for place_id, place in places.items():
            if place_id not in airport_info:
                airport_info[place_id] = {
                    "name": place.get("name", "Unknown"),
                    "iata": place.get("iata", "???"),
                    "latitude": place.get("coordinates", {}).get("latitude", 0.0),
                    "longitude": place.get("coordinates", {}).get("longitude", 0.0),
                }

        for quote in quotes.values():
            outbound = quote.get("outboundLeg", {})
            dest_id = outbound.get("destinationPlaceId")
            month = outbound.get("departureDateTime", {}).get("month", 0)
            amount = quote.get("minPrice", {}).get("amount")

            if not dest_id or not isinstance(month, int) or month <= 0:
                continue

            try:
                price = int(float(amount))
            except (TypeError, ValueError):
                continue

            prices_by_dest_month[dest_id][month].append(price)

    monthly_avg: dict[str, dict[int, float]] = {}
    for dest_id, months in prices_by_dest_month.items():
        monthly_avg[dest_id] = {}
        for month, price_list in months.items():
            monthly_avg[dest_id][month] = round(sum(price_list) / len(price_list), 2)

    lines: list[str] = []
    lines.append(";;; Auto-generated from monthly TXT files")
    lines.append(";;; Preu = mitjana del preu mínim de vols des de BCN per mes")
    lines.append("")
    lines.append("(definstances MAIN::travel-data")
    lines.append("")

    lines.append("    ;;; --- LOCATIONS ---")
    written_locs = set()
    for dest_id in monthly_avg:
        if dest_id not in airport_info:
            continue
        info = airport_info[dest_id]
        iata = info["iata"]
        if iata in written_locs:
            continue
        written_locs.add(iata)

        lines.append(f"    ([loc-{safe_id(iata)}] of Location")
        lines.append(f"        (latitude {info['latitude']})")
        lines.append(f"        (longitude {info['longitude']})")
        lines.append("        (continent X)")
        lines.append(f"        (country \"{info['name']}\")")
        lines.append(f"        (address \"{info['name']}\")")
        lines.append(f"        (district \"{iata}\"))")
        lines.append("")

    lines.append("    ;;; --- DESTINATIONS ---")
    written_dests = set()
    for dest_id in monthly_avg:
        if dest_id not in airport_info:
            continue
        info = airport_info[dest_id]
        iata = info["iata"]
        if iata in written_dests:
            continue
        written_dests.add(iata)

        lines.append(f"    ([dest-{safe_id(iata)}] of Destination")
        lines.append("        (hasClimate X) (hasTemperature X)")
        lines.append("        (hasBeach X) (hasMountain X)")
        lines.append("        (hasTypePopulation X)")
        lines.append("        (hasCulture X) (hasParty X) (hasActivities X)")
        lines.append("        (hasHistory X) (hasNature X)")
        lines.append(f"        (location [loc-{safe_id(iata)}]))")
        lines.append("")

    lines.append("    ;;; --- OFFERS (avg flight price per month) ---")
    offer_count = 0
    covered_months = set()
    for dest_id, months in monthly_avg.items():
        if dest_id not in airport_info:
            continue
        iata = airport_info[dest_id]["iata"]

        for month, avg_price in sorted(months.items()):
            month_name = MONTH_NAMES.get(month, f"M{month}")
            lines.append(f"    ([offer-{safe_id(iata)}-{month_name}] of Offer")
            lines.append(f"        (price {int(avg_price)})")
            lines.append("        (duration 7)")
            lines.append(f"        (month {month})")
            lines.append("        (priceLevel X)")
            lines.append("        (travelTime X)")
            lines.append(f"        (Destination [dest-{safe_id(iata)}]))")
            lines.append("")
            offer_count += 1
            covered_months.add(month)

    lines.append(")")
    lines.append("")

    with open(OUTPUT_CLIPS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    expected_months = set(range(1, 13))
    missing_by_name = sorted(expected_months - months_from_names)

    print(f"Generat: {OUTPUT_CLIPS}")
    print(f"Fitxers mensuals llegits: {len(month_files)}")
    print(f"Destins unics: {len(written_dests)}")
    print(f"Ofertes totals: {offer_count}")
    print(f"Mesos coberts per dades: {sorted(covered_months)}")
    if missing_by_name:
        print(f"Mesos sense fitxer .txt detectat: {missing_by_name}")


if __name__ == "__main__":
    main()