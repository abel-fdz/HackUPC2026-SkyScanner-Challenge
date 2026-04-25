import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
from datetime import date, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.app import generar_respuesta_chatbot

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SkyScanner Dream Destiny", page_icon="✈️", layout="centered")

def st_airplanes():
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

# --- ESTILOS ---
st.markdown("""
    <style>
    .stTextArea textarea {
        border-radius: 30px !important;
        border: 2px solid #ff4b4b !important;
        padding: 20px !important;
    }
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    .destino-card {
        background-color: #f9f9f9; border-radius: 16px;
        padding: 16px; text-align: center; border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)


# --- CABECERA ---
st.title("✈️ SkyScanner Dream Destiny")
st.caption("Encuentra el viaje perfecto según tus sueños")
st.divider()

# --- BUSCADOR DE VUELOS ---
st.subheader("🔍 Buscar vuelo")
col_origen, col_destino = st.columns(2)
AEROPUERTOS = [
    "Barcelona (BCN)", "Madrid (MAD)", "Londres (LHR)", "París (CDG)",
    "Roma (FCO)", "Ámsterdam (AMS)", "Berlín (BER)", "Lisboa (LIS)",
    "Nueva York (JFK)", "Tokio (NRT)", "Dubai (DXB)", "Cancún (CUN)"
]
with col_origen:
    origen = st.selectbox("🛫 Origen", AEROPUERTOS, index=0)
with col_destino:
    destino = st.selectbox("🛬 Destino", AEROPUERTOS, index=2)
col_ida, col_vuelta = st.columns(2)
with col_ida:
    fecha_ida = st.date_input("📅 Fecha de ida", value=date.today() + timedelta(days=30))
with col_vuelta:
    fecha_vuelta = st.date_input("📅 Fecha de vuelta", value=date.today() + timedelta(days=37))
col_pasajeros, col_clase = st.columns(2)
with col_pasajeros:
    pasajeros = st.number_input("👤 Pasajeros", min_value=1, max_value=9, value=1)
with col_clase:
    clase = st.selectbox("💺 Clase", ["Turista", "Business", "Primera clase"])
if st.button("🔎 Buscar vuelos"):
    if origen == destino:
        st.warning("El origen y el destino no pueden ser iguales.")
    elif fecha_vuelta < fecha_ida:
        st.warning("La fecha de vuelta no puede ser anterior a la de ida.")
    else:
        noches = (fecha_vuelta - fecha_ida).days
        st.info(f"Buscando vuelos de **{origen}** a **{destino}** · {noches} noches · {pasajeros} pasajero(s) · {clase}")
        st.toast("Búsqueda en curso...", icon="🔍")

st.divider()

# --- DESTINOS DESTACADOS ---
st.subheader("🌍 Destinos destacados")
destinos = [
    {"emoji": "🗼", "ciudad": "París",     "precio": "desde 189€", "desc": "La ciudad del amor"},
    {"emoji": "🏖️", "ciudad": "Bali",      "precio": "desde 620€", "desc": "Paraíso tropical"},
    {"emoji": "🗽", "ciudad": "Nueva York", "precio": "desde 399€", "desc": "La ciudad que nunca duerme"},
    {"emoji": "🏯", "ciudad": "Tokio",     "precio": "desde 710€", "desc": "Tradición y modernidad"},
    {"emoji": "🌅", "ciudad": "Santorini", "precio": "desde 240€", "desc": "Vistas al Egeo"},
    {"emoji": "🎭", "ciudad": "Roma",      "precio": "desde 140€", "desc": "La ciudad eterna"},
]
cols = st.columns(3)
for i, d in enumerate(destinos):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="destino-card">
            <div style="font-size: 2rem;">{d['emoji']}</div>
            <strong>{d['ciudad']}</strong><br>
            <span style="color: #ff4b4b; font-weight: bold;">{d['precio']}</span><br>
            <small style="color: gray;">{d['desc']}</small>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

st.divider()

# --- SECCIÓN IA: MODO LIBRE / MODO DETALLADO ---
st.subheader("🤖 Describe tu viaje ideal")
st.caption("Cuéntanos qué quieres y nuestra IA encontrará el destino perfecto para ti")

# Selector de modo
if "modo_detallado" not in st.session_state:
    st.session_state.modo_detallado = False

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("✏️ Modo libre", use_container_width=True):
        st.session_state.modo_detallado = False
with col_btn2:
    if st.button("🎛️ Modo detallado", use_container_width=True):
        st.session_state.modo_detallado = True

st.write("")

# --- MODO LIBRE ---
if not st.session_state.modo_detallado:
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
                respuesta = obtener_respuesta_ia(
                    user_text,
                    _config_params={"modo": "libre"},
                )
                st.markdown(respuesta)

            st.session_state.messages.append({"role": "assistant", "content": respuesta})

    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

# --- MODO DETALLADO ---
else:
    col1, col2 = st.columns(2)

    with col1:
        precio_max = st.slider("💶 Precio máximo (€/persona)", 100, 5000, 1500, step=50)
        duracion = st.slider("🗓️ Duración (días)", 1, 30, 7)
        temperatura = st.slider("🌡️ Temperatura deseada (°C)", 0, 45, 25)
        flexibilidad = st.slider("📅 Flexibilidad de fechas (±días)", 0, 30, 3)

    with col2:
        mes = st.selectbox("📆 Mes de viaje", [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        tipo_grupo = st.selectbox("👥 Tipo de viaje", [
            "Solo", "En pareja / Romántico", "Familia con niños",
            "Grupo de amigos", "Viaje de negocios"
        ])
        clima = st.selectbox("☁️ Clima preferido", [
            "Soleado y cálido", "Templado", "Frío / Nieve",
            "Tropical", "Seco / Desértico", "Sin preferencia"
        ])

    tipo_destino = st.multiselect(
        "🗺️ Tipo de destino",
        ["🏖️ Playa", "🏔️ Montaña", "🏙️ Gran metrópoli", "🏛️ Cultural / Museos",
         "🎉 Fiesta / Nightlife", "🧗 Aventura / Deporte", "🏰 Histórico"],
        default=["🏖️ Playa"]
    )

    if st.button("✨ Encontrar mi destino ideal"):
        tipos = ", ".join(tipo_destino) if tipo_destino else "Sin preferencia"
        texto_detallado = f"""
Precio máximo: {precio_max}€ por persona
Mes de viaje: {mes}
Duración: {duracion} días
Flexibilidad de fechas: ±{flexibilidad} días
Tipo de viaje: {tipo_grupo}
Clima preferido: {clima}
Temperatura deseada: {temperatura}°C
Tipo de destino: {tipos}
        """.strip()

        with st.spinner("Procesando..."):
            respuesta_detallado = obtener_respuesta_ia(
                texto_detallado,
                _config_params={"modo": "detallado"},
            )
        st.success("¡Proceso ejecutado!")
        st.markdown(respuesta_detallado)

st.divider()