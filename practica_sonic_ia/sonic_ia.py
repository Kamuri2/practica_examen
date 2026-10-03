import streamlit as st
import requests

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Sonic IA - Experto Musical", page_icon="🎸", layout="centered")

# ==========================================
# ESTILOS CSS Y PARTÍCULAS MUSICALES
# ==========================================
st.markdown("""
<style>
    /* Estilo Dark Metal */
    .stApp {
        background-color: #0d0d0d;
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .titulo {
        text-align: center;
        color: #ff1e56; /* Neon Crimson */
        font-family: 'Impact', fantasy;
        font-size: 3.5rem;
        text-shadow: 2px 2px 8px #ff1e56;
        margin-bottom: 0px;
    }
    
    .subtitulo {
        text-align: center;
        color: #b3b3b3;
        font-size: 1.2rem;
        margin-bottom: 30px;
        font-style: italic;
    }
    
    /* Botones estilo Metal */
    .stButton>button {
        background-color: #1a1a1a;
        color: #ff1e56;
        border: 1px solid #ff1e56;
        border-radius: 4px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff1e56;
        color: #0d0d0d;
        box-shadow: 0 0 10px #ff1e56;
    }
</style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components

# Inyección de JavaScript para que las partículas escapen los contenedores de Streamlit y se vean en toda la pantalla
components.html("""
<script>
    const doc = window.parent.document;
    
    // Eliminar si ya existen para no duplicar al recargar la app
    let existing = doc.getElementById('sonic-particles');
    if (existing) {
        existing.remove();
    }
    
    // Contenedor principal de partículas
    const container = doc.createElement('div');
    container.id = 'sonic-particles';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100vw';
    container.style.height = '100vh';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '999999';
    container.style.overflow = 'hidden';
    
    // Estilos de animacion
    const style = doc.createElement('style');
    style.innerHTML = `
        @keyframes floatUpSonic {
            0% { transform: translateY(110vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
        }
        @keyframes floatEmberSonic {
            0% { transform: translateY(110vh) translateX(0px) scale(1); opacity: 1; }
            50% { transform: translateY(50vh) translateX(20px) scale(1.2); opacity: 0.8; }
            100% { transform: translateY(-10vh) translateX(-20px) scale(0.5); opacity: 0; }
        }
        .sonic-particle {
            position: absolute;
            color: #ff1e56;
            font-size: 30px;
            opacity: 0.7;
            animation: floatUpSonic linear infinite;
        }
        .sonic-ember {
            position: absolute;
            width: 4px;
            height: 4px;
            background-color: #ff5722;
            border-radius: 50%;
            box-shadow: 0 0 8px #ff5722, 0 0 15px #ff9800;
            animation: floatEmberSonic linear infinite;
        }
    `;
    doc.head.appendChild(style);
    
    // 1. Generar iconos musicales
    const notas = ['🎵', '🎸', '🎶', '🥁', '🎹', '🎧', '🎼'];
    notas.forEach((nota, i) => {
        let el = doc.createElement('div');
        el.className = 'sonic-particle';
        el.innerText = nota;
        el.style.left = (10 + i * 13) + '%';
        el.style.animationDuration = (8 + (i % 5) * 2) + 's';
        el.style.animationDelay = ((i % 3) * 2) + 's';
        if(i % 2 === 0) el.style.color = '#8a2be2'; // Alternar colores
        container.appendChild(el);
    });
    
    // 2. Generar brazas de fuego
    for(let i=0; i<20; i++) {
        let el = doc.createElement('div');
        el.className = 'sonic-ember';
        el.style.left = (Math.random() * 100) + '%';
        el.style.animationDuration = (5 + Math.random() * 5) + 's';
        el.style.animationDelay = (Math.random() * 5) + 's';
        if(Math.random() > 0.5) {
            el.style.backgroundColor = '#ff9800';
            el.style.width = '6px';
            el.style.height = '6px';
        }
        container.appendChild(el);
    }
    
    doc.body.appendChild(container);
</script>
""", height=0, width=0)


# ==========================================
# FUNCIONES DEL LLM (Ollama)
# ==========================================
def consultar_ollama(mensajes):
    """Llama a la API local de Ollama usando el historial de mensajes."""
    url = "http://172.21.240.1:11434/api/chat"
    # System Prompt para Sonic IA (Experto en música, actitud rockera/metalera)
    payload = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "system", 
                "content": "Eres Sonic IA, un experto mundial en música de absolutamente todos los géneros (desde el Heavy Metal más oscuro hasta Música Clásica y Pop). Tienes una actitud intensa, apasionada y rockera. Respondes a las consultas musicales con datos curiosos, recomendaciones y mucha energía."
            }
        ] + mensajes,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error del servidor: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con Ollama: {e}"

def resumir_historial(mensajes):
    """Pide al LLM que resuma de qué se ha hablado en la sesión."""
    if len(mensajes) < 2:
        return "Aún no hemos hablado de música, ¡tira el primer riff!"
    
    prompt_resumen = "A continuación te doy el historial de nuestra charla musical. Haz un resumen muy breve y directo (máximo 3 viñetas) de las bandas, géneros o temas musicales de los que hemos hablado hoy. Historial: " + str(mensajes)
    
    url = "http://172.21.240.1:11434/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": prompt_resumen,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["response"]
        return "Error al generar resumen."
    except:
        return "Error de conexión."

# ==========================================
# INTERFAZ GRÁFICA (UI)
# ==========================================
st.markdown("<h1 class='titulo'>🎸 SONIC IA 🎸</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Tu oráculo musical definitivo. Rock, Metal, Jazz, y más...</p>", unsafe_allow_html=True)

# Inicializar el historial en la sesión
if "chat_musica" not in st.session_state:
    st.session_state.chat_musica = []

# Sidebar para el Resumen del Historial (Punto 3 del examen)
with st.sidebar:
    st.header("💿 Setlist (Tu Historial)")
    st.write("Genera un resumen rápido de los géneros y bandas que hemos discutido.")
    
    if st.button("🤘 Resumir Historial"):
        with st.spinner("Analizando la pista..."):
            resumen = resumir_historial(st.session_state.chat_musica)
            st.success("Resumen listo:")
            st.info(resumen)
    
    st.markdown("---")
    if st.button("🔥 Borrar Historial"):
        st.session_state.chat_musica = []
        st.rerun()

# Mostrar mensajes anteriores
for msg in st.session_state.chat_musica:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input del usuario
prompt_usuario = st.chat_input("Pregúntame sobre el origen del Black Metal, teoría de Jazz, o recomiéndame un disco...")

if prompt_usuario:
    # Mostrar la pregunta del usuario en la pantalla
    with st.chat_message("user"):
        st.write(prompt_usuario)
    
    # Guardar en historial
    st.session_state.chat_musica.append({"role": "user", "content": prompt_usuario})
    
    # Obtener respuesta del LLM
    with st.spinner("Sintonizando frecuencias..."):
        respuesta = consultar_ollama(st.session_state.chat_musica)
        
    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.write(respuesta)
        
    # Guardar en historial
    st.session_state.chat_musica.append({"role": "assistant", "content": respuesta})
