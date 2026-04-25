import argparse
import json
import os
import re
import time
from datetime import date
from pathlib import Path
from typing import Any

import requests


DEFAULT_ENDPOINT = "https://partners.api.skyscanner.net/apiservices/v1/hotels/indicative/search"
DEFAULT_INPUT = "2_instancias.clp"
DEFAULT_OUTPUT = "hotels_indicative_results.json"


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_locations_and_destinations(clp_path: Path) -> list[dict[str, Any]]:
    lines = clp_path.read_text(encoding="utf-8").splitlines()

    location_data: dict[str, dict[str, Any]] = {}
    destination_to_location: dict[str, str] = {}

    current_kind: str | None = None
    current_name: str | None = None
    current_buffer: list[str] = []

    def flush_current() -> None:
        nonlocal current_kind, current_name, current_buffer
        if not current_kind or not current_name:
            current_kind = None
            current_name = None
            current_buffer = []
            return

        block = " ".join(s.strip() for s in current_buffer)
        if current_kind == "Location":
            def _slot(pattern: str, default: Any = None) -> Any:
                m = re.search(pattern, block)
                return m.group(1).strip() if m else default

            location_data[current_name] = {
                "latitude": float(_slot(r"\(latitude\s+([-\d.]+)\)", "0.0")),
                "longitude": float(_slot(r"\(longitude\s+([-\d.]+)\)", "0.0")),
                "continent": _slot(r'\(continent\s+"([^"]+)"\)', "Unknown"),
                "country": _slot(r'\(country\s+"([^"]+)"\)', "Unknown"),
                "address": _slot(r'\(address\s+"([^"]+)"\)', "Unknown"),
                "district": _slot(r'\(district\s+"([^"]+)"\)', "Unknown"),
            }
        elif current_kind == "Destination":
            m = re.search(r"\(location\s+\[(loc-[^\]]+)\]\)", block)
            if m:
                destination_to_location[current_name] = m.group(1)

        current_kind = None
        current_name = None
        current_buffer = []

    for line in lines:
        stripped = line.strip()
        m_loc = re.match(r"^\(\[(loc-[^\]]+)\]\s+of\s+Location\b", stripped)
        m_dest = re.match(r"^\(\[(dest-[^\]]+)\]\s+of\s+Destination\b", stripped)

        if m_loc:
            flush_current()
            current_kind = "Location"
            current_name = m_loc.group(1)
            current_buffer = [stripped]
            if stripped.endswith("))"):
                flush_current()
            continue

        if m_dest:
            flush_current()
            current_kind = "Destination"
            current_name = m_dest.group(1)
            current_buffer = [stripped]
            if stripped.endswith("))"):
                flush_current()
            continue

        if current_kind:
            current_buffer.append(stripped)
            if stripped.endswith("))"):
                flush_current()

    flush_current()

    destinations: list[dict[str, Any]] = []
    for dest_name, loc_name in destination_to_location.items():
        slug = dest_name.replace("dest-", "")
        destinations.append(
            {
                "destination_instance": dest_name,
                "slug": slug,
                "location_instance": loc_name,
                "location": location_data.get(loc_name, {}),
            }
        )

    return destinations


def month_to_checkin_checkout(year: int, month: int, stay_nights: int) -> tuple[dict[str, int], dict[str, int]]:
    checkin = date(year, month, 15)
    checkout_ord = checkin.toordinal() + max(1, stay_nights)
    checkout = date.fromordinal(checkout_ord)
    return (
        {"year": checkin.year, "month": checkin.month, "day": checkin.day},
        {"year": checkout.year, "month": checkout.month, "day": checkout.day},
    )


def build_payload(
    destination: dict[str, Any],
    month: int,
    year: int,
    nights: int,
    market: str,
    locale: str,
    currency: str,
    adults: int,
    rooms: int,
) -> dict[str, Any]:
    checkin, checkout = month_to_checkin_checkout(year, month, nights)
    loc = destination["location"]

    # Generic request body for the Hotels Indicative endpoint.
    # If your account needs different field names, use --payload-template to adapt quickly.
    return {
        "query": {
            "market": market,
            "locale": locale,
            "currency": currency,
            "searchCriteria": {
                "checkInDate": checkin,
                "checkOutDate": checkout,
                "rooms": rooms,
                "adults": adults,
            },
            "destination": {
                "name": loc.get("country") or destination["slug"],
                "coordinates": {
                    "latitude": loc.get("latitude", 0.0),
                    "longitude": loc.get("longitude", 0.0),
                },
                "district": loc.get("district", ""),
            },
        }
    }


def request_indicative(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
    timeout_seconds: int,
) -> tuple[int, Any]:
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
    }
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout_seconds)
    body: Any
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    return resp.status_code, body


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Skyscanner Hotels Indicative prices for each destination in 2_instancias.clp and each month."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to .clp instances file.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output JSON file path.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Hotels Indicative endpoint URL.")
    parser.add_argument("--year", type=int, default=date.today().year, help="Year to query.")
    parser.add_argument("--nights", type=int, default=7, help="Stay length in nights.")
    parser.add_argument("--market", default="ES")
    parser.add_argument("--locale", default="es-ES")
    parser.add_argument("--currency", default="EUR")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--rooms", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--sleep-ms", type=int, default=200, help="Delay between API calls.")
    parser.add_argument("--dry-run", action="store_true", help="Build payloads without calling API.")
    args = parser.parse_args()

    workspace = Path.cwd()
    load_dotenv(workspace / ".env")

    # Following your instruction:
    # x-api-key is read from SKYSCANNER_INDICATIVE_BASE_URL.
    # Fallback to SKYSCANNER_API_KEY for convenience if the former is not present.
    api_key = os.getenv("SKYSCANNER_INDICATIVE_BASE_URL", "").strip() or os.getenv("SKYSCANNER_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        raise RuntimeError(
            "Missing API key. Set SKYSCANNER_INDICATIVE_BASE_URL (as requested) or SKYSCANNER_API_KEY in .env."
        )

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    destinations = parse_locations_and_destinations(input_path)
    if not destinations:
        raise RuntimeError(f"No Destination instances found in {input_path}")

    results: dict[str, Any] = {
        "meta": {
            "endpoint": args.endpoint,
            "input": str(input_path),
            "year": args.year,
            "nights": args.nights,
            "market": args.market,
            "locale": args.locale,
            "currency": args.currency,
            "adults": args.adults,
            "rooms": args.rooms,
            "dry_run": args.dry_run,
            "destinations_count": len(destinations),
            "months_per_destination": 12,
        },
        "results": [],
    }

    for dest in destinations:
        for month in range(1, 13):
            payload = build_payload(
                destination=dest,
                month=month,
                year=args.year,
                nights=args.nights,
                market=args.market,
                locale=args.locale,
                currency=args.currency,
                adults=args.adults,
                rooms=args.rooms,
            )

            row: dict[str, Any] = {
                "destination_instance": dest["destination_instance"],
                "destination_slug": dest["slug"],
                "location_instance": dest["location_instance"],
                "month": month,
                "payload": payload,
            }

            if args.dry_run:
                row["status_code"] = None
                row["response"] = None
            else:
                status_code, response = request_indicative(
                    endpoint=args.endpoint,
                    api_key=api_key,
                    payload=payload,
                    timeout_seconds=args.timeout,
                )
                row["status_code"] = status_code
                row["response"] = response
                time.sleep(max(0, args.sleep_ms) / 1000.0)

            results["results"].append(row)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(results['results'])} rows to {output_path}")


if __name__ == "__main__":
    main()
