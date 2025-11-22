import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import asyncio

# Importar el MISMO orquestador que usa la API
from app.graph.workflow import run_extraction
from app.core.telemetry import configure_telemetry

# Configuración inicial
load_dotenv()
st.set_page_config(page_title="OpsBot: PDF Intelligence", page_icon="🤖", layout="wide")
configure_telemetry() # Configurar LangSmith al cargar

# --- UI Header ---
st.title("🤖 OpsBot: Extractor Inteligente v1")
st.markdown("""
Esta herramienta utiliza **LangGraph** para orquestar la extracción de datos.
El mismo motor alimenta la API que conecta con Power Automate.
""")

# --- Sidebar: Estado del Sistema ---
with st.sidebar:
    st.header("🔧 Estado del Sistema")
    if os.getenv("OPENAI_API_KEY"):
        st.success("✅ OpenAI API Key detectada")
    else:
        st.error("❌ Falta OPENAI_API_KEY")
    
    if os.getenv("LANGCHAIN_API_KEY"):
        st.info("📡 LangSmith Tracing activo")

# --- Main Area: Upload ---
uploaded_file = st.file_uploader("Sube un contrato o reporte (PDF)", type=["pdf"])

if uploaded_file:
    st.divider()
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info(f"📄 Archivo: {uploaded_file.name}")
    
    # Botón de acción
    if st.button("🚀 Ejecutar Análisis (LangGraph)"):
        with st.spinner("Ejecutando grafo de extracción... (Parsing -> Reasoning -> Summary)"):
            try:
                # 1. Leer bytes (Streamlit devuelve un BytesIO, lo convertimos a bytes)
                # Nota: uploaded_file.read() mueve el cursor, si se reusa hay que hacer seek(0)
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                
                # 2. Invocar el grafo (Async wrapper para Streamlit)
                # metadata para LangSmith
                metadata = {"source": "streamlit_ui", "filename": uploaded_file.name}
                
                # Run async loop in sync context
                result = asyncio.run(run_extraction(file_bytes, metadata=metadata))
                
                if result.get("error"):
                    st.error(f"Error en el grafo: {result['error']}")
                else:
                    # 3. Mostrar Resultados
                    st.success("✅ Procesamiento completado")
                    
                    # Sección Resumen
                    st.subheader("📝 Resumen Ejecutivo (GPT-4o)")
                    st.info(result.get("summary"))
                    
                    # Sección Tablas
                    tables = result.get("extracted_tables", [])
                    if tables:
                        st.subheader(f"📊 Tablas Detectadas ({len(tables)})")
                        for i, table_data in enumerate(tables):
                            with st.expander(f"Tabla #{i+1}"):
                                # Convertir lista de listas a DataFrame si es necesario
                                if isinstance(table_data, list):
                                    df = pd.DataFrame(table_data[1:], columns=table_data[0])
                                else:
                                    df = table_data
                                st.dataframe(df)
                    else:
                        st.warning("No se detectaron tablas estructuradas.")

                    # Sección Texto Crudo (Debug)
                    with st.expander("🔍 Ver Texto Crudo Extraído"):
                        st.text(result.get("extracted_text"))

            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {str(e)}")
                # Imprimir stacktrace en consola para el dev
                import traceback
                traceback.print_exc()