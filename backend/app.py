import sys
import os
import re
import json
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from backend.prompts import (
    TEXT_PROMPT_DEFAULT,
    IMAGE_PROMPT_TEMPLATE,
    CLIPS_EXPLANATION_PROMPT_TEMPLATE,
)
from backend.clips_bridge import run_clips_from_preferences_json
from backend.instances_generator import DESTINATION_CATALOG


SKYSCANNER_FLIGHTS_BASE_URL = os.getenv(
    "SKYSCANNER_FLIGHTS_BASE_URL",
    "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search",
).strip()


def cargar_configuracion():
    """Carga configuración desde .env en la raíz del proyecto."""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    base_prompt = TEXT_PROMPT_DEFAULT.strip()

    return api_key, model_name, base_prompt


def construir_candidatos_modelo(model_name: str) -> list[str]:
    """Genera candidatos de modelo evitando duplicados."""
    candidatos = []
    if model_name:
        candidatos.extend([model_name, f"models/{model_name}"])
    candidatos.extend(
        [
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
        ]
    )
    seen = set()
    resultado = []
    for c in candidatos:
        if c not in seen:
            seen.add(c)
            resultado.append(c)
    return resultado


def _consultar_gemini(contents) -> str:
    """Ejecuta llamada a Gemini con fallback de modelos."""
    api_key, model_name, base_prompt = cargar_configuracion()
    if not api_key:
        return "Falta GEMINI_API_KEY en el archivo .env"

    client = genai.Client(api_key=api_key)
    ultimo_error = ""
    hubo_error_cuota = False
    for modelo in construir_candidatos_modelo(model_name):
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=contents,
            )
            response_text = getattr(response, "text", None)
            if response_text and response_text.strip():
                return response_text.strip()
            return "Gemini no devolvió texto en la respuesta."
        except Exception as exc:
            error_text = str(exc)
            ultimo_error = f"Error con modelo '{modelo}': {error_text}"
            if "429" in error_text or "quota" in error_text.lower():
                hubo_error_cuota = True
                # Probamos otro modelo por si la cuota varía por modelo/proyecto.
                continue
            if "404" in error_text or "not found" in error_text.lower():
                # Probamos el siguiente modelo candidato.
                continue
            return ultimo_error

    if hubo_error_cuota:
        return (
            "No puedo consultar Gemini ahora mismo porque tu proyecto no tiene cuota disponible "
            "(error 429). Revisa facturacion/cuotas en Google AI Studio."
        )

    return f"No encontré un modelo Gemini disponible. Último detalle: {ultimo_error}"


def generar_respuesta_chatbot(user_text: str) -> str:
    """Llama a Gemini con prompt base + texto del usuario."""
    cleaned_text = user_text.strip()
    if not cleaned_text:
        return "No recibí texto del usuario."

    _, _, base_prompt = cargar_configuracion()
    final_prompt = (
        f"{base_prompt}\n\n"
        f"Texto del usuario:\n{cleaned_text}\n\n"
        "Responde en espanol y en formato claro."
    )
    return _consultar_gemini(final_prompt)


def generar_respuesta_imagen_chatbot(image_bytes: bytes, mime_type: str, user_text: str = "") -> str:
    """Analiza imagen + contexto y devuelve JSON de keywords de destino."""
    if not image_bytes:
        return "No recibi imagen para analizar."

    contexto = user_text.strip() or "No hay texto adicional del usuario."
    prompt_imagen = IMAGE_PROMPT_TEMPLATE.format(contexto_usuario=contexto)
    contents = [
        prompt_imagen,
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"),
    ]
    return _consultar_gemini(contents)


def generar_recomendacion_clips_desde_json(preferences_json: str) -> str:
    """Bridge backend: JSON preferences -> CLIPS output."""
    return run_clips_from_preferences_json(preferences_json)


def generar_explicacion_usuario_desde_clips(preferences_json: str, clips_output: str) -> str:
    """
    Convierte la salida tecnica de CLIPS en una explicacion natural para usuario final.
    """
    if not (clips_output or "").strip():
        return "No hay salida de CLIPS para explicar."

    prompt = CLIPS_EXPLANATION_PROMPT_TEMPLATE.format(
        preferences_json=(preferences_json or "").strip(),
        clips_output=(clips_output or "").strip(),
    )
    raw = _consultar_gemini(prompt)
    return _normalizar_explicacion(raw)


def _normalizar_explicacion(texto: str) -> str:
    """
    Limpia repeticiones exactas de parrafos para mejorar legibilidad.
    """
    if not texto:
        return texto
    bloques = [b.strip() for b in texto.split("\n\n") if b.strip()]
    seen = set()
    out = []
    for b in bloques:
        k = re.sub(r"\s+", " ", b).strip().lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(b)
    return "\n\n".join(out)


def _json_loads_loose(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def extraer_destinos_desde_clips(clips_output: str) -> list[dict]:
    """
    Extrae destinos sugeridos por CLIPS a partir de lineas tipo:
    '1. offer-rome ...'
    """
    if not clips_output:
        return []

    catalog_by_slug = {d["slug"]: d for d in DESTINATION_CATALOG}
    seen = set()
    result = []
    # Soporta formatos tipo:
    # "1. offer-rome", "1. [offer-rome]", "1) offer-rome"
    origin_iata = "BCN"
    for match in re.findall(r"\b\d+[.)]\s+\[?([A-Za-z0-9_-]+)\]?", clips_output):
        name = match.strip().lower()
        slug = name.replace("offer-", "")
        if slug in seen:
            continue
        if slug not in catalog_by_slug:
            continue
        seen.add(slug)
        d = catalog_by_slug[slug]
        if d.get("iata") == origin_iata:
            continue
        result.append(
            {
                "slug": slug,
                "city": d["city"],
                "iata": d["iata"],
                "country": d["country"],
            }
        )
    if result:
        return result

    # Fallback: detectar por nombre de ciudad en texto CLIPS.
    low = clips_output.lower()
    for d in DESTINATION_CATALOG:
        if d["city"].lower() in low and d["slug"] not in seen:
            if d.get("iata") == origin_iata:
                continue
            seen.add(d["slug"])
            result.append(
                {
                    "slug": d["slug"],
                    "city": d["city"],
                    "iata": d["iata"],
                    "country": d["country"],
                }
            )
    return result


def _build_travel_date(month: int) -> date:
    m = month if 1 <= month <= 12 else date.today().month
    year = date.today().year
    if m < date.today().month:
        year += 1
    return date(year, m, 15)


def _fetch_live_flights_top3(origin_iata: str, dest_iata: str, travel_date: date, budget_max: float | None):
    import requests

    api_key = os.getenv("SKYSCANNER_API_KEY", "").strip()
    if not api_key:
        return []
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
                    "date": {"year": travel_date.year, "month": travel_date.month, "day": travel_date.day},
                }
            ],
            "adults": 1,
            "cabinClass": "CABIN_CLASS_ECONOMY",
        }
    }
    try:
        create = requests.post(f"{SKYSCANNER_FLIGHTS_BASE_URL}/create", json=payload, headers=headers, timeout=20)
        if create.status_code != 200:
            return []
        token = create.json().get("sessionToken")
        if not token:
            return []
        poll = requests.post(f"{SKYSCANNER_FLIGHTS_BASE_URL}/poll/{token}", headers=headers, timeout=20)
        if poll.status_code != 200:
            return []
        data = poll.json()
        content = data.get("content", {})
        results = content.get("results", {})
        itineraries = results.get("itineraries", {})
        sorting = content.get("sortingOptions", {})
        cheapest = sorting.get("cheapest", [])

        out = []
        for item in cheapest:
            itin_id = item.get("itineraryId")
            itin = itineraries.get(itin_id, {})
            options = itin.get("pricingOptions", [])
            best_price = None
            for opt in options:
                amount = opt.get("price", {}).get("amount")
                if amount is not None:
                    eur = float(amount) / 1000.0
                    if best_price is None or eur < best_price:
                        best_price = eur
            if best_price is None:
                continue
            if budget_max is not None and best_price > budget_max:
                continue
            leg_ids = itin.get("legIds", [])
            legs = results.get("legs", {})
            duration = None
            stops = None
            if leg_ids:
                leg = legs.get(leg_ids[0], {})
                duration = leg.get("durationInMinutes")
                stops = leg.get("stopCount")
            out.append(
                {
                    "price_eur": round(best_price, 2),
                    "duration_min": duration,
                    "stops": stops,
                }
            )
            if len(out) >= 3:
                break
        return out
    except Exception:
        return []


def obtener_live_opciones_destino(preferences_json: str, destination_slug: str) -> dict:
    """
    Devuelve top 3 vuelos para destino seleccionado.
    """
    catalog_by_slug = {d["slug"]: d for d in DESTINATION_CATALOG}
    dest = catalog_by_slug.get((destination_slug or "").strip().lower())
    if not dest:
        return {"error": f"Destino no encontrado en catalogo: {destination_slug}"}

    try:
        prefs = _json_loads_loose(preferences_json)
    except Exception:
        prefs = {}

    origin_iata = "BCN"
    month = int(prefs.get("travel_month") or date.today().month)
    duration = int(prefs.get("trip_duration_days") or 7)
    budget_total = prefs.get("maximum_total_budget_eur")
    budget_total = float(budget_total) if budget_total is not None else None
    per_component_budget = (budget_total / 2.0) if budget_total else None

    travel_date = _build_travel_date(month)

    flights = _fetch_live_flights_top3(origin_iata, dest["iata"], travel_date, per_component_budget)
    return {
        "destination": {
            "slug": dest["slug"],
            "city": dest["city"],
            "iata": dest["iata"],
            "country": dest["country"],
            "month": month,
            "trip_duration_days": duration,
        },
        "flights_top3": flights,
    }


if __name__ == "__main__":
    # El frontend envía el texto como argumento de línea de comandos.
    user_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    respuesta = generar_respuesta_chatbot(user_text)
    print(respuesta)