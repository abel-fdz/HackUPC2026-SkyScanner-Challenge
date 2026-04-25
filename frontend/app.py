import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
from datetime import date, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.app import generar_respuesta_chatbot, generar_respuesta_imagen_chatbot


# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

AEROPUERTOS = [
    "Barcelona (BCN)", "Madrid (MAD)", "Londres (LHR)", "París (CDG)",
    "Roma (FCO)", "Ámsterdam (AMS)", "Berlín (BER)", "Lisboa (LIS)",
    "Nueva York (JFK)", "Tokio (NRT)", "Dubai (DXB)", "Cancún (CUN)"
]

DESTINOS_DESTACADOS = [
    {"emoji": "🗼", "ciudad": "París",     "precio": "desde 189€", "desc": "La ciudad del amor"},
    {"emoji": "🏖️", "ciudad": "Bali",      "precio": "desde 620€", "desc": "Paraíso tropical"},
    {"emoji": "🗽", "ciudad": "Nueva York", "precio": "desde 399€", "desc": "La ciudad que nunca duerme"},
    {"emoji": "🏯", "ciudad": "Tokio",     "precio": "desde 710€", "desc": "Tradición y modernidad"},
    {"emoji": "🌅", "ciudad": "Santorini", "precio": "desde 240€", "desc": "Vistas al Egeo"},
    {"emoji": "🎭", "ciudad": "Roma",      "precio": "desde 140€", "desc": "La ciudad eterna"},
]

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

TIPOS_VIAJE = [
    "Solo", "En pareja / Romántico", "Familia con niños",
    "Grupo de amigos", "Viaje de negocios"
]

CLIMAS = [
    "Soleado y cálido", "Templado", "Frío / Nieve",
    "Tropical", "Seco / Desértico", "Sin preferencia"
]

TIPOS_DESTINO = [
    "🏖️ Playa", "🏔️ Montaña", "🏙️ Gran metrópoli", "🏛️ Cultural / Museos",
    "🎉 Fiesta / Nightlife", "🧗 Aventura / Deporte", "🏰 Histórico"
]

COLORES_CLIMA = {
    "Soleado y cálido":   ("linear-gradient(to bottom, #FFDAB9, #FFA07A, #FF6347)"),
    "Templado":           ("linear-gradient(to bottom, #d4f1c4, #89c96e, #4a9e3f)"),
    "Frío / Nieve":       ("linear-gradient(to bottom, #e8f4fd, #b8d9f0, #7ab8e8)"),
    "Tropical":           ("linear-gradient(to bottom, #c8f5a0, #40c0a0, #0077b6)"),
    "Seco / Desértico":   ("linear-gradient(to bottom, #f5e6c8, #e0b96e, #c47a2a)"),
    "Sin preferencia":    ("linear-gradient(to bottom, #0d1b2e, #0d2137, #0d2840)"),
}


# ============================================================================
# FUNCIONES DE CONFIGURACIÓN Y ESTILOS
# ============================================================================

def configurar_pagina():
    """Configura los parámetros básicos de la página Streamlit."""
    st.set_page_config(page_title="SkyScanner Dream Destiny", page_icon="✈️", layout="centered")
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
    

def aplicar_estilos(clima="Sin preferencia"):
    gradiente = COLORES_CLIMA.get(clima, COLORES_CLIMA["Sin preferencia"])
    st.markdown(f"""
        <style>
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

@st.cache_data(show_spinner="Consultando a nuestro experto...")
def obtener_respuesta_ia(texto_usuario, _config_params=None):
    # _config_params permite invalidar cache cuando cambie configuración relevante.
    try:
        respuesta = generar_respuesta_chatbot(texto_usuario)
        if "429" in respuesta or "cuota disponible" in respuesta.lower():
            return "Lo siento, la IA esta temporalmente en limite de cuota. Intentalo de nuevo en un minuto."
        return respuesta
    except Exception as exc:
        return f"Error inesperado al consultar la IA: {exc}"


@st.cache_data(show_spinner="Analizando imagen con IA...")
def obtener_respuesta_ia_imagen(image_bytes, mime_type, texto_usuario="", _config_params=None):
    try:
        respuesta = generar_respuesta_imagen_chatbot(image_bytes, mime_type, texto_usuario)
        if "429" in respuesta or "cuota disponible" in respuesta.lower():
            return "Lo siento, la IA esta temporalmente en limite de cuota. Intentalo de nuevo en un minuto."
        return respuesta
    except Exception as exc:
        return f"Error inesperado al analizar la imagen: {exc}"


def mostrar_cabecera():
    """Muestra el encabezado de la página."""
    st.title("✈️ SkyScanner Dream Destiny")
    st.caption("Encuentra el viaje perfecto según tus sueños")
    st.divider()


# ============================================================================
# FUNCIONES DE MODO IA (LIBRE Y DETALLADO)
# ============================================================================

def inicializar_sesion():
    """Inicializa las variables de sesión necesarias."""
    if "modo_detallado" not in st.session_state:
        st.session_state.modo_detallado = False


def mostrar_selector_modo():
    """Muestra los botones para seleccionar modo texto o imagen."""
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✏️ Modo texto", use_container_width=True):
            st.session_state.modo_detallado = False
    with col_btn2:
        if st.button("📸 Modo imagen", use_container_width=True):
            st.session_state.modo_detallado = True


def seccion_modo_texto():
    """Muestra la sección del modo texto de entrada de texto."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.text_area(
        label="¿Cómo imaginas tu viaje perfecto?",
        placeholder=(
            "Ej: Quiero un viaje de 10 días con mi pareja, me gustan las playas "
            "tranquilas, la buena comida y no quiero gastar más de 2000 EUR por persona..."
        ),
        height=200,
    )
    if st.button("✨ Encontrar mi destino ideal"):
        if not user_text.strip():
            st.warning("Cuéntanos algo sobre tu viaje ideal primero.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                with placeholder.container():
                    st_airplanes()
                respuesta = obtener_respuesta_ia(
                    user_text,
                    _config_params={"modo": "libre"},
                )
                placeholder.markdown(respuesta)

            st.session_state.messages.append({"role": "assistant", "content": respuesta})
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()




def seccion_modo_imagen():
    """Muestra la sección del modo imagen."""
    st.write("")
    imagen = st.file_uploader(
        "📸 Sube una imagen que inspire tu viaje",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if imagen:
        st.image(imagen, caption="Tu imagen de inspiración", use_container_width=True)

    texto_contexto = st.text_area(
        "Contexto opcional para la IA (qué te inspira de la imagen)",
        placeholder="Ej: Quiero un destino con este estilo, relajado y no muy caro.",
        height=100,
        key="imagen_contexto_texto",
    )

    if st.button("✨ Encontrar mi destino ideal"):
        if not imagen:
            st.warning("Sube una imagen primero.")
        else:
            placeholder = st.empty()
            with placeholder.container():
                st_airplanes()
            respuesta_json = obtener_respuesta_ia_imagen(
                imagen.getvalue(),
                getattr(imagen, "type", "image/jpeg"),
                texto_contexto,
                _config_params={"modo": "imagen"},
            )
            placeholder.success("Analisis completado")
            placeholder.code(respuesta_json, language="json")

def seccion_ia():
    """Maneja la sección de IA con modos libre y detallado."""
    st.subheader("🤖 Describe tu viaje ideal")
    st.caption("Cuéntanos qué quieres y nuestra IA encontrará el destino perfecto para ti")

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
    clima_actual = st.session_state.get("clima_seleccionado", "Sin preferencia")
    aplicar_estilos(clima_actual)

    mostrar_cabecera()
    seccion_ia()


if __name__ == "__main__":
    main()