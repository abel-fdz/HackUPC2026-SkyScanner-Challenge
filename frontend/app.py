import streamlit as st
import streamlit.components.v1 as components
import subprocess
import sys
from pathlib import Path

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SkyScanner Dream Destiny", page_icon="✈️", layout="centered")

# --- FUNCIÓN MODO FIESTA (AVIONES) ---
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

# --- FUNCIÓN BACKEND ---
def mi_funcion_provisional(texto):
    backend_script = Path(__file__).parent.parent / "backend" / "proceso.py"
    
    # DEBUG: Verifica si el archivo existe de verdad
    if not backend_script.exists():
        st.error(f"Archivo no encontrado en: {backend_script}")
        return

    with st.spinner("Procesando..."):
        result = subprocess.run(
            [sys.executable, str(backend_script), texto],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

    # DEBUG: Vamos a ver TODO lo que devolvió el objeto result
    # st.write(result) # Descomenta esto para ver el objeto completo

    if result.returncode == 0:
        st.success("¡Proceso ejecutado!")
        
        # Forzamos a ver qué hay, aunque sea espacios en blanco
        if result.stdout:
            st.code(result.stdout, language="text")
        else:
            st.warning("El script se ejecutó bien, pero la salida (stdout) está vacía. ¿Tiene prints el backend?")
            
        # Por si acaso el error se fue a stderr a pesar de tener returncode 0
        if result.stderr:
            st.subheader("Aviso en stderr:")
            st.info(result.stderr)
    else:
        st.error(f"Error código {result.returncode}")
        st.code(result.stderr)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stTextArea textarea {
        border-radius: 30px !important;
        border: 2px solid #ff4b4b !important;
        padding: 20px !important;
    }
    .stButton button {
        border-radius: 20px;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración Extra")
    activar_fiesta = st.toggle("Activar modo fiesta 🥳")
    if activar_fiesta:
        st_airplanes()
        st.caption("Aviones en camino...")

# --- CONTENIDO PRINCIPAL ---
st.title("¡Hola, Usuario! 👋")

user_text = st.text_area(
    label="Introduce tu mensaje aquí:",
    placeholder="Escribe algo increíble...",
    height=300
)

if st.button("Ejecutar proceso"):
    mi_funcion_provisional(user_text)