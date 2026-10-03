import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import os
from fpdf import FPDF
import plotly.express as px
from streamlit_option_menu import option_menu
from app.database import db
from app.rules import evaluate_rules
from app.llm import clasificar_incidente_llm, consultar_rag

st.set_page_config(page_title="Logística Inteligente", layout="wide", initial_sidebar_state="expanded")

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

img_base64 = get_base64_of_bin_file("logo.jpg")

st.markdown(f"""
    <style>
    /* Estilos Generales */
    .stApp {{ background-color: #0b0c10; color: #c5c6c7; font-family: 'Segoe UI', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid #1f2833; padding-top: 1rem; }}
    h1, h2, h3 {{ color: #d4a373 !important; }}
    
    .stButton>button {{ background-color: #d4a373; color: #0b0c10; border-radius: 8px; border: none; font-weight: 800; padding: 0.5rem 1rem; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    .stButton>button:hover {{ background-color: #b5835a; color: #ffffff; transform: translateY(-2px); }}
    
    div[data-baseweb="select"] > div, input, textarea {{ background-color: #1f2833 !important; color: #ffffff !important; border: 1px solid #45a29e !important; border-radius: 8px !important; }}
    [data-testid="stMetricValue"] {{ color: #d4a373 !important; }}
    
    .header-container {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid #1f2833; padding-bottom: 1rem; }}
    .header-text h1 {{ margin: 0; padding: 0; font-size: 2.5rem; color: #ffffff !important; letter-spacing: 1px; }}
    .header-text p {{ color: #d4a373; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; margin: 0; margin-top: 5px; font-weight: bold; }}
    .header-logo {{ width: 100px; height: 100px; border-radius: 50%; border: 2px solid #d4a373; box-shadow: 0 0 15px rgba(212, 163, 115, 0.3); }}
    
    /* Ocultar padding innecesario en la barra */
    [data-testid="stSidebarNav"] {{
        display: none;
    }}
    /* Quitar el fondo del iframe de option-menu en versiones nuevas de streamlit */
    iframe {{
        background-color: transparent !important;
    }}
    /* Tarjeta de resultados LLM */
    .llm-card {{
        background-color: #1f2833;
        border-left: 5px solid #d4a373;
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }}
    </style>
""", unsafe_allow_html=True)

if img_base64:
    st.markdown(f"""
        <div class="header-container">
            <div class="header-text">
                <h1>LOGÍSTICA INTELIGENTE</h1>
                <p>Centro de Control y Evaluaciones</p>
            </div>
            <img src="data:image/jpeg;base64,{img_base64}" class="header-logo">
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("LOGÍSTICA INTELIGENTE")

if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []

# Menú lateral dinámico y animado con streamlit-option-menu
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    menu = option_menu(
        menu_title=None,
        options=[
            "Panel de Control", 
            "Gestión de Camiones",
            "Simulador de Accesos", 
            "Bandeja de Incidentes", 
            "Asistente IA (RAG)", 
            "Matriz de Riesgos", 
            "Configuración"
        ],
        icons=["bar-chart-fill", "truck", "stoplights", "envelope-paper", "robot", "shield-exclamation", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#050505"},
            "icon": {"color": "#d4a373", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "12px", 
                "text-align": "left", 
                "margin": "5px 10px", 
                "--hover-color": "#121212", 
                "color": "#ffffff", 
                "font-weight": "bold", 
                "border-radius": "12px",
                "text-transform": "uppercase",
                "padding": "15px 20px"
            },
            "nav-link-selected": {
                "background-color": "#1c1714", 
                "color": "#ffffff", 
                "border": "1px solid #8b6b50"
            },
        }
    )

if menu == "Panel de Control":
    st.header("📊 Panel de Control Principal")
    
    st.markdown("### Filtros Globales")
    col_f1, col_f2 = st.columns(2)
    with col_f1: fecha_inicio = st.date_input("Fecha Inicio", datetime.now() - timedelta(days=30))
    with col_f2: fecha_fin = st.date_input("Fecha Fin", datetime.now())
        
    start_dt = datetime.combine(fecha_inicio, datetime.min.time())
    end_dt = datetime.combine(fecha_fin, datetime.max.time())
    query = {"marca_tiempo": {"$gte": start_dt, "$lte": end_dt}}

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Accesos Autorizados", db.accesos.count_documents(query))
    col2.metric("Incidentes Reportados", db.incidentes.count_documents({"estado": "nuevo", "marca_tiempo": {"$gte": start_dt, "$lte": end_dt}}))
    col3.metric("Riesgos Críticos (Impacto > 3)", db.riesgos_eticos.count_documents({"impacto": {"$gte": 4}}))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    pipeline = [{"$match": query}, {"$group": {"_id": "$clasificacion.categoria", "count": {"$sum": 1}}}]
    agregacion = list(db.incidentes.aggregate(pipeline))
    if agregacion:
        df_agg = pd.DataFrame(agregacion).rename(columns={"_id": "Categoría", "count": "Cantidad"})
        fig = px.bar(df_agg, x='Categoría', y='Cantidad', color='Categoría', text='Cantidad',
                     title="Distribución de Incidentes por Categoría", template="plotly_dark",
                     color_discrete_sequence=['#d4a373', '#b5835a', '#8b6b50', '#e07a5f'])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5c6c7"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay incidentes en este periodo para graficar.")

    st.markdown("### Exportar Reportes")
    df_export = pd.DataFrame(list(db.incidentes.find(query, {"_id": 0})))
    if not df_export.empty:
        col_b1, col_b2, col_b3 = st.columns(3)
        df_str = df_export.copy()
        df_str["clasificacion"] = df_str["clasificacion"].astype(str)
        
        with col_b1:
            st.download_button("📄 Descargar CSV", data=df_str.to_csv(index=False), file_name="reporte.csv", mime="text/csv")
        with col_b2:
            st.download_button("📋 Descargar JSON", data=df_export.to_json(orient="records", date_format="iso"), file_name="reporte.json", mime="application/json")
        with col_b3:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Reporte General de Incidentes", ln=True, align="C")
            pdf.set_font("Arial", size=10)
            for idx, row in df_export.iterrows():
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(200, 8, txt=f"--- Registro ---", ln=True)
                pdf.set_font("Arial", size=9)
                pdf.multi_cell(0, 5, txt=f"Fecha: {row.get('marca_tiempo','')}")
                pdf.multi_cell(0, 5, txt=f"Estado: {row.get('estado','')}")
                pdf.multi_cell(0, 5, txt=f"Correo: {row.get('correo_original','')}")
                pdf.multi_cell(0, 5, txt=f"Clasificación: {row.get('clasificacion','')}")
                pdf.ln(3)
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📕 Descargar PDF", data=pdf_bytes, file_name="reporte.pdf", mime="application/pdf")
    else:
        st.warning("No hay datos para exportar en este rango.")

elif menu == "Gestión de Camiones":
    st.header("🚛 Directorio de Flota y Padrón")
    with st.expander("➕ Formulario para Nuevo Camión"):
        with st.form("form_camion"):
            placa = st.text_input("Placa (Ej. ABC-123)")
            camion_id = st.text_input("ID Interno (Ej. TRK-001)")
            empresa = st.text_input("Empresa Proveedora")
            col1, col2 = st.columns(2)
            with col1: autorizacion = st.checkbox("Autorización Vigente", value=True)
            with col2: certificacion = st.checkbox("Certificación del Conductor", value=True)
                
            if st.form_submit_button("Registrar en MongoDB"):
                if placa and camion_id and empresa:
                    if db.camiones.find_one({"placa": placa}):
                        st.error("Ya existe un camión con esa placa.")
                    else:
                        db.camiones.insert_one({"placa": placa, "camion_id": camion_id, "empresa": empresa, "autorizacion": autorizacion, "certificacion_conductor": certificacion})
                        st.success("Camión registrado exitosamente en la base de datos.")
                else:
                    st.error("Por favor completa los campos principales.")
    
    st.markdown("### Tabla de Vehículos Registrados")
    camiones = list(db.camiones.find({}, {"_id": 0}))
    if camiones:
        df_camiones = pd.DataFrame(camiones)
        st.dataframe(df_camiones, use_container_width=True)
        st.markdown("### Baja de Vehículos")
        col_del, _ = st.columns(2)
        with col_del:
            placa_del = st.selectbox("Selecciona Placa a Eliminar", [c["placa"] for c in camiones])
            if st.button("🗑️ Eliminar Definitivamente"):
                db.camiones.delete_one({"placa": placa_del})
                st.success(f"Camión {placa_del} eliminado de la flota.")
                st.rerun()
    else:
        st.info("No hay camiones registrados.")

elif menu == "Simulador de Accesos":
    st.header("🚦 Simulador de Lógica Computacional")
    st.markdown("Prueba el motor de reglas evaluando compuertas booleanas en tiempo real.")
    
    camiones_cursor = db.camiones.find({}, {"placa": 1})
    lista_placas = [doc["placa"] for doc in camiones_cursor if "placa" in doc]
    if not lista_placas: lista_placas = ["SIM-001"]
        
    placa_simulada = st.selectbox("Seleccionar Vehículo Objetivo", lista_placas)
    
    col1, col2 = st.columns(2)
    with col1:
        P = st.toggle("P: Permiso de acceso validado", value=True)
        S = st.toggle("S: Inspección de seguridad aprobada", value=True)
        V = st.toggle("V: Certificación del conductor vigente", value=True)
    with col2:
        Q = st.toggle("Q: Alerta activa de reporte de robo", value=False)
        R = st.toggle("R: Carga de material peligroso", value=False)
        H = st.toggle("H: Dentro del horario permitido", value=True)
        
    A, E, explicacion = evaluate_rules(P, Q, R, S, V, H)
    
    st.markdown("### Salida del Motor de Inferencia")
    res_col1, res_col2 = st.columns(2)
    if A: res_col1.success("✅ **A = TRUE** (Acceso Concedido)")
    else: res_col1.error("⛔ **A = FALSE** (Acceso Denegado)")
    if E: res_col2.warning("⚠️ **E = TRUE** (Inspección Especial Requerida)")
    else: res_col2.info("🛡️ **E = FALSE** (Inspección Rutinaria)")
        
    st.info(f"**Justificación de Reglas:** {explicacion}")
    
    if st.button("💾 Guardar Evento en Bitácora"):
        db.accesos.insert_one({"placa": placa_simulada, "P": P, "Q": Q, "R": R, "S": S, "V": V, "H": H, "resultado_A": A, "resultado_E": E, "explicacion": explicacion, "marca_tiempo": datetime.now(), "operador": "demo"})
        st.success("Evento registrado exitosamente.")

elif menu == "Bandeja de Incidentes":
    st.header("📧 Procesador NLP de Correos")
    st.markdown("Convierte reportes de texto libre en JSON estructurado usando el LLM de Ollama.")
    correo = st.text_area("Pegue el reporte del operador aquí:", height=150)
    
    if st.button("🧠 Procesar con Ollama"):
        with st.spinner("Analizando sintaxis y contexto..."):
            resultado, latencia, raw, error = clasificar_incidente_llm(correo)
            if error:
                st.error(f"Fallo en comunicación LLM. Razón: {error}")
                cat_manual = "Accidente" if "choque" in correo.lower() else "Otro"
                db.incidentes.insert_one({"correo_original": correo, "estado": "nuevo", "clasificacion_manual": cat_manual, "metodo": "fallback", "marca_tiempo": datetime.now()})
                st.warning(f"Activando sistema de respaldo. Clasificado como: {cat_manual}")
            else:
                st.success(f"Procesamiento exitoso (Tiempo: {latencia:.2f}s)")
                
                datos = resultado.model_dump()
                color_prio = "#e07a5f" if datos.get('prioridad') == "Alta" else ("#d4a373" if datos.get('prioridad') == "Media" else "#81b29a")
                
                html_card = f"""
                <div class='llm-card'>
                    <h3 style='margin-top: 0; color: #ffffff;'>📑 Ficha del Incidente Procesada</h3>
                    <table style='width: 100%; text-align: left; margin-bottom: 15px;'>
                        <tr>
                            <td><b>Categoría Extraída:</b></td>
                            <td><span style='background-color: #2b3b4d; padding: 4px 8px; border-radius: 4px;'>{datos.get('categoria', 'N/A')}</span></td>
                        </tr>
                        <tr>
                            <td><b>Nivel de Prioridad:</b></td>
                            <td><span style='color: {color_prio}; font-weight: bold;'>{datos.get('prioridad', 'N/A').upper()}</span></td>
                        </tr>
                    </table>
                    <b>Entidades Detectadas:</b><br>
                """
                
                if datos.get('entidades'):
                    for ent in datos.get('entidades'):
                        html_card += f"<span style='display:inline-block; background-color: #45a29e; color: #0b0c10; padding: 2px 8px; border-radius: 12px; margin: 3px; font-weight: bold; font-size: 12px;'>{ent}</span>"
                else:
                    html_card += "<i>(Ninguna)</i>"
                    
                html_card += f"""
                    <br><br><b>Resumen Ejecutivo:</b>
                    <p style='color: #c5c6c7; font-style: italic; border-left: 3px solid #66fcf1; padding-left: 10px;'>"{datos.get('resumen', 'N/A')}"</p>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                
                db.incidentes.insert_one({"correo_original": correo, "estado": "nuevo", "clasificacion": resultado.model_dump(), "metodo": "llm", "marca_tiempo": datetime.now()})
                db.evaluaciones_llm.insert_one({"prompt": correo, "respuesta": raw, "modelo": "llama3.2", "latencia": latencia, "coincidio_reglas": True, "marca_tiempo": datetime.now()})

elif menu == "Asistente IA (RAG)":
    st.header("🤖 Interfaz Conversacional de Consulta")
    st.markdown("Pregunta al sistema. La IA cruzará datos de MongoDB (Camiones, Bitácora, Incidentes).")
    for msj in st.session_state.historial_chat:
        st.chat_message(msj["rol"]).write(msj["texto"])
        
    pregunta = st.chat_input("Ej: Genera un reporte textual de los incidentes de hoy.")
    if pregunta:
        st.chat_message("user").write(pregunta)
        st.session_state.historial_chat.append({"rol": "user", "texto": pregunta})
        
        c_acc = "".join([f"- Fecha: {a['marca_tiempo']}, Placa: {a.get('placa', 'N/A')}, Aprobado: {a['resultado_A']}, Motivo: {a['explicacion']}\n" for a in list(db.accesos.find().sort("marca_tiempo", -1).limit(40))])
        c_inc = "".join([f"- Fecha: {i['marca_tiempo']}, Estado: {i['estado']}, Correo: {i['correo_original']}\n" for i in list(db.incidentes.find().sort("marca_tiempo", -1).limit(40))])
        c_hist = "".join([f"{m['rol'].upper()}: {m['texto']}\n" for m in st.session_state.historial_chat[-5:]])

        with st.spinner("Buscando en la base de datos..."):
            respuesta = consultar_rag(f"Contexto:\n{c_acc}\n{c_inc}\nHistorial:\n{c_hist}\nPregunta: {pregunta}", c_acc+c_inc)
            
        st.chat_message("assistant").write(respuesta)
        st.session_state.historial_chat.append({"rol": "assistant", "texto": respuesta})

elif menu == "Matriz de Riesgos":
    st.header("⚖️ Análisis de Riesgos Éticos de IA")
    
    with st.expander("➕ Declarar Nuevo Riesgo"):
        with st.form("form_riesgo"):
            mod = st.text_input("Módulo")
            desc = st.text_area("Descripción del Riesgo")
            cat = st.selectbox("Categoría Técnica", ["Sesgo Algorítmico", "Privacidad de Datos", "Alucinación de IA", "Dependencia Tecnológica", "Otro"])
            prob = st.slider("Probabilidad (1-5)", 1, 5, 3)
            imp = st.slider("Impacto (1-5)", 1, 5, 3)
            miti = st.text_area("Plan de Mitigación")
            if st.form_submit_button("Registrar en Matriz"):
                db.riesgos_eticos.insert_one({"modulo": mod, "descripcion": desc, "categoria": cat, "probabilidad": prob, "impacto": imp, "mitigacion": miti})
                st.success("Guardado.")
                
    riesgos = list(db.riesgos_eticos.find({}, {"_id":0}))
    if riesgos:
        df = pd.DataFrame(riesgos)
        df['Nivel_Riesgo'] = df['probabilidad'] * df['impacto']
        
        st.markdown("### Mapa de Calor Profesional")
        fig = px.scatter(df, x='probabilidad', y='impacto', size='Nivel_Riesgo', color='categoria', hover_name='modulo', hover_data=['descripcion', 'mitigacion'], title="Matriz de Riesgos", template="plotly_dark", size_max=40, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5c6c7"))
        fig.update_xaxes(range=[0, 6])
        fig.update_yaxes(range=[0, 6])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Datos Crudos")
        st.dataframe(df, use_container_width=True)

elif menu == "Configuración":
    st.header("⚙️ Ajustes del Sistema y Modelos")
    nuevo_modelo = st.text_input("Modelo de Ollama", "llama3.2")
    if st.button("Aplicar"):
        st.success(f"Modelo '{nuevo_modelo}' guardado.")
