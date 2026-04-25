import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from backend.prompts import TEXT_PROMPT_DEFAULT, IMAGE_PROMPT_TEMPLATE
from backend.clips_bridge import run_clips_from_preferences_json


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


if __name__ == "__main__":
    # El frontend envía el texto como argumento de línea de comandos.
    user_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    respuesta = generar_respuesta_chatbot(user_text)
    print(respuesta)