import streamlit as st
import streamlit.components.v1 as components
import sys
import re
import html
import unicodedata
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.app import (
    generar_respuesta_chatbot,
    generar_respuesta_imagen_chatbot,
    generar_recomendacion_clips_desde_json,
)


# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

AEROPUERTOS = [
    "Barcelona (BCN)", "Madrid (MAD)", "London (LHR)", "Paris (CDG)",
    "Rome (FCO)", "Amsterdam (AMS)", "Berlin (BER)", "Lisbon (LIS)",
    "New York (JFK)", "Tokyo (NRT)", "Dubai (DXB)", "Cancun (CUN)"
]

DESTINOS_DESTACADOS = [
    {"emoji": "🗼", "ciudad": "Paris",     "precio": "from 189€", "desc": "The city of love"},
    {"emoji": "🏖️", "ciudad": "Bali",      "precio": "from 620€", "desc": "Tropical paradise"},
    {"emoji": "🗽", "ciudad": "New York",   "precio": "from 399€", "desc": "The city that never sleeps"},
    {"emoji": "🏯", "ciudad": "Tokyo",     "precio": "from 710€", "desc": "Tradition and modernity"},
    {"emoji": "🌅", "ciudad": "Santorini", "precio": "from 240€", "desc": "Aegean views"},
    {"emoji": "🎭", "ciudad": "Rome",      "precio": "from 140€", "desc": "The eternal city"},
]

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

TIPOS_VIAJE = [
    "Solo", "Couple / Romantic", "Family with children",
    "Group of friends", "Business trip"
]

CLIMAS = [
    "Sunny and warm", "Mild", "Cold / Snow",
    "Tropical", "Dry / Desert", "No preference"
]

INSTANCES_PATH = PROJECT_ROOT / "2_instancias.clp"

TIPOS_DESTINO = [
    "🏖️ Beach", "🏔️ Mountain", "🏙️ Big city", "🏛️ Culture / Museums",
    "🎉 Party / Nightlife", "🧗 Adventure / Sports", "🏰 Historic"
]

COLORES_CLIMA = {
    "Sunny and warm":     ("linear-gradient(to bottom, #FFDAB9, #FFA07A, #FF6347)"),
    "Mild":               ("linear-gradient(to bottom, #d4f1c4, #89c96e, #4a9e3f)"),
    "Cold / Snow":        ("linear-gradient(to bottom, #e8f4fd, #b8d9f0, #7ab8e8)"),
    "Tropical":           ("linear-gradient(to bottom, #c8f5a0, #40c0a0, #0077b6)"),
    "Dry / Desert":       ("linear-gradient(to bottom, #f5e6c8, #e0b96e, #c47a2a)"),
    "No preference":      ("linear-gradient(to bottom, #0d1b2e, #0d2137, #0d2840)"),
}


# ============================================================================
# FUNCIONES DE CONFIGURACIÓN Y ESTILOS
# ============================================================================

def configurar_pagina():
    """Configura los parámetros básicos de la página Streamlit."""
    st.set_page_config(page_title="SkyScanner Dream Destiny", page_icon="✈️", layout="wide")
    st.markdown("""
        <style>
        /* Fondo de la aplicación principal */
        .stApp {
            background-color: #0e1117 !important;
            color: #fafafa !important;
        }
        
        /* Fondo de la barra lateral */
        [data-testid="stSidebar"] {
            background-color: #262730 !important;
        }
        
        /* Asegurar que el texto sea legible */
        h1, h2, h3, p, label {
            color: #fafafa !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # Inyectar CSS para ocultar el menú de opciones y la marca de agua
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    

def aplicar_estilos(clima="No preference"):
    gradiente = COLORES_CLIMA.get(clima, COLORES_CLIMA["No preference"])
    st.markdown(f"""
        <style>
        .block-container {{
            max-width: 77rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }}
        .recommendations-wrap {{
            max-width: 920px;
            margin-left: auto;
            margin-right: auto;
        }}
        .stApp {{
            background: {gradiente};
        }}
        .stTextArea textarea {{
            border-radius: 30px !important;
            border: 1px solid #3d4050 !important;
            padding: 20px !important;
        }}
        .stTextArea textarea:focus {{
            border-color: #3d4050 !important;
            box-shadow: none !important;
        }}
        /* Ocultar el mensaje "Press Ctrl+Enter" */
        .stTextArea [data-testid="InputInstructions"] {{
            display: none !important;
        }}
        .stButton button {{
            border-radius: 20px;
            width: 100%;
            font-weight: bold;
            background-color: #0066CC !important;
            color: #fafafa !important;
            border: 1px solid #0055aa !important;
        }}
        .stButton button:hover {{
            background-color: #0055aa !important;
            border-color: #004488 !important;
        }}
        [data-testid="stFileUploaderDropzone"] {{
            background-color: #1a1d27 !important;
            border-color: #3d4050 !important;
        }}
        [data-testid="stFileUploaderDropzone"] button {{
            background-color: #2d3144 !important;
            color: #9ba3b8 !important;
            border: 1px solid #3d4050 !important;
        }}
        .destino-card {{
            background-color: #1a1d27; border-radius: 16px;
            padding: 16px; text-align: center; border: 1px solid #3d4050;
            color: #fafafa;
        }}
        .destino-card strong {{
            color: #fafafa !important;
        }}
        .destino-card small {{
            color: #9ba3b8 !important;
        }}
        [data-testid="stFileUploaderDropzone"] span {{
            color: #9ba3b8 !important;
        }}
        .stTextArea textarea {{
            border-radius: 30px !important;
            border: 1px solid #3d4050 !important;
            padding: 20px !important;
            background-color: #1a1d27 !important;
            color: #fafafa !important;
        }}
        .stTextArea textarea::placeholder {{
            color: #9ba3b8 !important;
        }}
        /* Estilos para bloque de código */
        [data-testid="stCode"] {{
            background-color: #1a1d27 !important;
        }}
        [data-testid="stCode"] pre {{
            background-color: #1a1d27 !important;
            color: #fafafa !important;
        }}
        [data-testid="stCode"] code {{
            background-color: #1a1d27 !important;
            color: #fafafa !important;
        }}
        .hljs {{
            background-color: #1a1d27 !important;
            color: #fafafa !important;
        }}
        /* Estilos para spinner/loader */
        .stSpinner {{
            color: #fafafa !important;
        }}
        [data-testid="stSpinner"] {{
            color: #fafafa !important;
        }}
        .element-container [role="status"] {{
            color: #fafafa !important;
        }}
        /* Spinner SVG */
        .stSpinner svg {{
            stroke: #fafafa !important;
        }}
        [role="status"] svg {{
            stroke: #fafafa !important;
        }}
        </style>
        """, unsafe_allow_html=True)

def st_airplanes():
    """Anima aviones cayendo desde la parte superior de la pantalla."""
    components.html("""
    <script>
      const parent = window.parent.document;
      const style = parent.createElement('style');
      style.id = 'airplane-style';
      style.textContent = `
        .st-airplane {
          position: fixed !important;
          pointer-events: none !important;
          z-index: 999999 !important;
          opacity: 0;
          animation: st-rise linear forwards;
        }
        @keyframes st-rise {
          0%   { opacity: 0; transform: translateY(0); }
          8%   { opacity: 1; }
          88%  { opacity: 1; }
          100% { opacity: 0; transform: translateY(-110vh); }
        }
      `;
      parent.head.appendChild(style);
      const emojis = ['✈️', '🛫', '🛩️'];
      const count  = 38;
      for (let i = 0; i < count; i++) {
        setTimeout(() => {
          const p = parent.createElement('div');
          p.className = 'st-airplane';
          p.textContent = emojis[Math.floor(Math.random() * emojis.length)];
          p.style.fontSize = (20 + Math.random() * 20) + 'px';
          p.style.left = (Math.random() * 100) + 'vw';
          p.style.top  = '100vh';
          const dur   = 2.0 + Math.random() * 1.6;
          const delay = Math.random() * 1.5;
          p.style.animationDuration = dur + 's';
          p.style.animationDelay   = delay + 's';
          parent.body.appendChild(p);
          setTimeout(() => {
            p.remove();
            if (i === count - 1) style.remove();
          }, (dur + delay + 0.6) * 1000);
        }, i * 100);
      }
    </script>
    """, height=0)

@st.cache_data(show_spinner="Listening deeply to your dreams, so your journey can find you...")
def obtener_respuesta_ia(texto_usuario, _config_params=None):
    # _config_params permite invalidar cache cuando cambie configuración relevante.
    try:
        respuesta = generar_respuesta_chatbot(texto_usuario)
        if "429" in respuesta or "cuota disponible" in respuesta.lower():
            return "Sorry, the AI is temporarily rate-limited. Please try again in a minute."
        return respuesta
    except Exception as exc:
        return f"Unexpected error while querying the AI: {exc}"


@st.cache_data(show_spinner="Running CLIPS engine...")
def obtener_salida_clips(preferences_json, _config_params=None):
    try:
        return generar_recomendacion_clips_desde_json(preferences_json)
    except Exception as exc:
        return f"Unexpected error while running CLIPS: {exc}"


def render_clips_output_elegant(clips_output: str):
    """
    Renderiza salida CLIPS con formato legible:
    - Primera línea como título
    - Resto como texto normal
    - Ventajas en verde y desventajas en rojo
    """
    raw_lines = [ln.strip() for ln in (clips_output or "").splitlines() if ln.strip()]
    lines = [
        ln
        for ln in raw_lines
        if not re.fullmatch(r"[=\-]{8,}", ln)
    ]
    if not lines:
        st.info("CLIPS returned no content.")
        return

    title = lines[0]
    body_lines = lines[1:]

    st.markdown(
        f"<h2 style='font-size: 3.0rem; line-height: 1.12; margin: 0.2rem 0 0.65rem 0; font-weight: 800;'>{html.escape(title)}</h2>",
        unsafe_allow_html=True,
    )
    if not body_lines:
        return

    def _render_tag_balls_combined(good_items: list[str], bad_items: list[str]):
        paired = [("good", it) for it in good_items] + [("bad", it) for it in bad_items]
        if not paired:
            return
        chips = ""
        for tone, item in paired:
            bg = "#dcfce7" if tone == "good" else "#fee2e2"
            fg = "#166534" if tone == "good" else "#991b1b"
            border = "#86efac" if tone == "good" else "#fca5a5"
            chips += (
                f"<span style='display:inline-block; margin:0 8px 8px 0; padding:6px 12px; "
                f"border-radius:999px; background:{bg}; color:{fg}; border:1px solid {border}; "
                f"font-size:0.86rem; white-space:nowrap;'>{html.escape(item)}</span>"
            )
        st.markdown(f"<div style='margin: 0.15rem 0 0.35rem 0;'>{chips}</div>", unsafe_allow_html=True)

    # Group lines by destination block to render each destination together.
    blocks = []
    current = []
    for line in body_lines:
        if re.match(r"^\d+\.\s+", line):
            if current:
                blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    if not blocks:
        blocks = [body_lines]

    for block in blocks:
        header = block[0] if block else ""
        if header and re.match(r"^\d+\.\s+", header):
            st.markdown(
                f"<p style='margin: 0.62rem 0 0.42rem; font-size: 1.36rem; line-height: 1.35; font-weight: 800;'>"
                f"{html.escape(header)}</p>",
                unsafe_allow_html=True,
            )

        normal_lines = []
        advantages_items = []
        disadvantages_items = []

        for line in block[1:] if header else block:
            low = line.lower()
            if re.search(r"\b(ventajas?|advantages?|pros?)\b", low):
                tail = re.split(r"[:：]", line, maxsplit=1)
                content = tail[1] if len(tail) > 1 else line
                advantages_items.extend(
                    [x.strip(" -") for x in re.split(r",|;|\|", content) if x.strip(" -")]
                )
            elif re.search(r"\b(desventajas?|disadvantages?|contras?)\b", low):
                tail = re.split(r"[:：]", line, maxsplit=1)
                content = tail[1] if len(tail) > 1 else line
                disadvantages_items.extend(
                    [x.strip(" -") for x in re.split(r",|;|\|", content) if x.strip(" -")]
                )
            elif re.search(r"\b(reason|motivo)\b", low):
                # Hide reason field as requested.
                continue
            else:
                normal_lines.append(line)

        for line in normal_lines:
            st.markdown(
                f"<p style='margin: 0.32rem 0; font-size: 1.05rem; line-height: 1.55;'>"
                f"{html.escape(line)}</p>",
                unsafe_allow_html=True,
            )

        # Requested: all tags in one single row, keeping each tag color.
        _render_tag_balls_combined(advantages_items, disadvantages_items)


def _normalize_text(value: str) -> str:
    txt = unicodedata.normalize("NFKD", value)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return txt.strip().lower()


@st.cache_data(show_spinner=False)
def _load_location_index():
    """
    Carga un índice de países/destinos con coordenadas desde 2_instancias.clp.
    """
    if not INSTANCES_PATH.exists():
        return {}

    raw = INSTANCES_PATH.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"\(\[loc-[^\]]+\] of Location\s*"
        r"\n\s*\(latitude ([^)]+)\)\s*"
        r"\n\s*\(longitude ([^)]+)\)\s*"
        r"\n\s*\(continent [^)]+\)\s*"
        r"\n\s*\(country \"([^\"]+)\"\)",
        re.MULTILINE,
    )

    index = {}
    for match in pattern.finditer(raw):
        lat = float(match.group(1))
        lon = float(match.group(2))
        country = match.group(3)
        index[_normalize_text(country)] = {"name": country, "lat": lat, "lon": lon}
    return index


def _extract_top_destination_names(clips_output: str):
    """
    Extrae destinos del TOP amb format flexible.
    """
    names = []
    for line in clips_output.splitlines():
        line = line.strip()
        if not re.match(r"^\d+\.\s+", line):
            continue

        # Treure prefix "1. "
        candidate = re.sub(r"^\d+\.\s+", "", line).strip()

        # Retallar pel començament del bloc de grade si existeix.
        candidate = re.split(r"\s+\*{1,3}\s*", candidate, maxsplit=1)[0].strip()
        candidate = re.split(r"\s+NOT SUITABLE\b", candidate, maxsplit=1)[0].strip()

        # Treure codi oferta entre claudators.
        candidate = re.sub(r"\s*\[offer-[^\]]+\]\s*", " ", candidate, flags=re.IGNORECASE).strip()

        # Treure el mes al final si apareix com "(JAN)" etc.
        candidate = re.sub(r"\s+\([A-Z]{3}\)\s*$", "", candidate).strip()

        if candidate:
            names.append(candidate)
    return names


def render_recommendations_map(clips_output: str):
    names = _extract_top_destination_names(clips_output)
    if not names:
        st.info("Could not extract destination names from the TOP list to plot the map.")
        return

    loc_index = _load_location_index()
    rows = []
    for name in names:
        hit = loc_index.get(_normalize_text(name))
        if hit:
            rows.append({"Destination": hit["name"], "lat": hit["lat"], "lon": hit["lon"]})

    if not rows:
        st.info("TOP destinations were found, but they could not be mapped to coordinates.")
        return

    st.markdown("### 🗺️ Recommended destinations map")
    st.caption("Pins for destinations that appear in the top recommendations.")

    df = pd.DataFrame(rows)
    st.map(df, latitude="lat", longitude="lon")


def render_clips_and_live_block(preferences_json: str, source_tag: str):
    st.markdown('<div class="recommendations-wrap">', unsafe_allow_html=True)
    clips_output = obtener_salida_clips(
        preferences_json,
        _config_params={"modo": source_tag},
    )
    render_clips_output_elegant(clips_output)
    render_recommendations_map(clips_output)
    st.markdown("</div>", unsafe_allow_html=True)


@st.cache_data(show_spinner="Analyzing image with AI...")
def obtener_respuesta_ia_imagen(image_bytes, mime_type, texto_usuario="", _config_params=None):
    try:
        respuesta = generar_respuesta_imagen_chatbot(image_bytes, mime_type, texto_usuario)
        if "429" in respuesta or "cuota disponible" in respuesta.lower():
            return "Sorry, the AI is temporarily rate-limited. Please try again in a minute."
        return respuesta
    except Exception as exc:
        return f"Unexpected error while analyzing the image: {exc}"


def mostrar_cabecera():
    """Muestra el encabezado de la página."""
    st.markdown(
        "<h1 style='font-size:4.0rem; line-height: 1.1; margin-bottom: 0.2rem;'>✈️ SkyScanner Dream Destiny</h1>",
        unsafe_allow_html=True,
    )
    st.caption("Find the perfect trip based on your dreams")
    st.divider()


# ============================================================================
# FUNCIONES DE MODO IA (LIBRE Y DETALLADO)
# ============================================================================

def inicializar_sesion():
    """Inicializa las variables de sesión necesarias."""
    if "modo_detallado" not in st.session_state:
        st.session_state.modo_detallado = False
    if "respuesta_ia_imagen" not in st.session_state:
        st.session_state.respuesta_ia_imagen = ""
    if "ultima_respuesta_texto" not in st.session_state:
        st.session_state.ultima_respuesta_texto = ""


def mostrar_selector_modo():
    """Muestra los botones para seleccionar modo texto o imagen."""
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✏️ Text mode", use_container_width=True):
            st.session_state.modo_detallado = False
    with col_btn2:
        if st.button("📸 Image mode", use_container_width=True):
            st.session_state.modo_detallado = True


def seccion_modo_texto():
    """Muestra la sección del modo texto de entrada de texto."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message.get("role") == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])

    user_text = st.text_area(
        label="How do you imagine your perfect trip?",
        placeholder=(
            "Example: I want a 10-day trip with my partner, I like peaceful beaches, "
            "great food, and I do not want to spend more than 2000 EUR per person..."
        ),
        height=200,
    )
    _, submit_col = st.columns([3, 1])
    with submit_col:
        trigger_text_mode = st.button("✨ Find my ideal destination", use_container_width=True)
    if trigger_text_mode:
        if not user_text.strip():
            st.warning("Tell us something about your ideal trip first.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)

            placeholder = st.empty()
            with placeholder.container():
                st_airplanes()
            respuesta = obtener_respuesta_ia(
                user_text,
                _config_params={"modo": "libre"},
            )
            st.session_state.ultima_respuesta_texto = respuesta
            clips_output = obtener_salida_clips(
                respuesta,
                _config_params={"modo": "texto"},
            )
            placeholder.empty()

    if st.session_state.ultima_respuesta_texto:
        render_clips_and_live_block(st.session_state.ultima_respuesta_texto, "texto")

def seccion_modo_imagen():
    """Muestra la sección del modo imagen."""
    st.write("")
    imagen = st.file_uploader(
        "📸 Upload an image that inspires your trip",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if imagen:
        st.image(imagen, caption="Your inspiration image", use_container_width=True)

    texto_contexto = st.text_area(
        "Optional context for AI (what inspires you from the image)",
        placeholder="Example: I want a destination with this style, relaxing and not too expensive.",
        height=100,
        key="imagen_contexto_texto",
    )

    _, submit_col = st.columns([3, 1])
    with submit_col:
        trigger_image_mode = st.button("✨ Find my ideal destination", use_container_width=True)
    if trigger_image_mode:
        if not imagen:
            st.warning("Upload an image first.")
        else:
            placeholder = st.empty()
            with placeholder.container():
                st_airplanes()
            st.session_state.respuesta_ia_imagen = obtener_respuesta_ia_imagen(
                imagen.getvalue(),
                getattr(imagen, "type", "image/jpeg"),
                texto_contexto,
                _config_params={"modo": "imagen"},
            )
    if st.session_state.respuesta_ia_imagen:
        st.success("Analysis completed")
        render_clips_and_live_block(st.session_state.respuesta_ia_imagen, "imagen")

def seccion_ia():
    """Maneja la sección de IA con modos libre y detallado."""
    st.subheader("Describe your ideal trip")
    st.caption("Tell us what you want and our AI will find the perfect destination for you")

    inicializar_sesion()
    mostrar_selector_modo()
    st.write("")

    if not st.session_state.modo_detallado:
        seccion_modo_texto()
    else:
        seccion_modo_imagen()

    st.divider()


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal que coordina la ejecución de la aplicación."""
    configurar_pagina()
    inicializar_sesion()
    clima_actual = st.session_state.get("clima_seleccionado", "No preference")
    aplicar_estilos(clima_actual)

    mostrar_cabecera()
    seccion_ia()


if __name__ == "__main__":
    main()