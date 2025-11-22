import os
import tempfile
from typing import TypedDict, List, Any, Optional, Dict
from langgraph.graph import StateGraph, END

# Importamos las herramientas puras que movimos a la capa 'tools'
from app.tools.pdf_parser import (
    extract_text_single_page,
    extract_tables_single_page,
    extract_total_pages
)

# Cliente de OpenAI para la síntesis
from openai import OpenAI

# --- 1. Definición del Estado del Agente ---
class AgentState(TypedDict):
    """
    Define la estructura de datos que viaja a través del grafo.
    Todos los nodos leen y escriben en este diccionario compartido.
    """
    file_bytes: bytes          # Input: El archivo PDF crudo
    metadata: Dict[str, Any]   # Input: Datos extra (nombre archivo, fuente, etc.)
    
    extracted_text: str        # Output intermedio: Texto consolidado
    extracted_tables: List[Any]# Output intermedio: Tablas detectadas
    
    summary: str               # Output final: Resumen generado por IA
    error: Optional[str]       # Manejo de errores

# --- 2. Definición de Nodos (Pasos del Proceso) ---

def parse_pdf_node(state: AgentState) -> AgentState:
    """
    NODO 1: Ingesta y Extracción.
    Toma los bytes del PDF, utiliza las herramientas de `pdf_parser` y 
    extrae el contenido crudo.
    """
    print("--- 🔄 NODE: Parsing PDF ---")
    
    # Si ya hay un error previo, saltamos
    if state.get("error"):
        return state

    tmp_path = None
    try:
        # 1. Guardar bytes en archivo temporal para procesamiento seguro
        # (pdfplumber maneja mejor paths para aperturas múltiples que streams)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(state["file_bytes"])
            tmp_path = tmp.name

        # 2. Ejecutar extracción usando las herramientas de 'app/tools'
        total_pages = extract_total_pages(tmp_path)
        text_content = []
        all_tables = []

        print(f"   📄 Procesando {total_pages} páginas...")

        for i in range(total_pages):
            # A. Extraer Texto
            page_text = extract_text_single_page(tmp_path, i)
            text_content.append(f"--- Página {i+1} ---\n{page_text}")

            # B. Extraer Tablas
            tables, strategy = extract_tables_single_page(tmp_path, i)
            if tables:
                for df in tables:
                    # Convertimos DataFrame a dict para que sea serializable en el estado
                    # Formato simple: {"columns": [...], "data": [[...], [...]]}
                    table_data = {
                        "page": i + 1,
                        "columns": df.columns.tolist(),
                        "data": df.values.tolist()
                    }
                    all_tables.append(table_data)

        # 3. Actualizar el estado con los resultados
        return {
            "extracted_text": "\n\n".join(text_content),
            "extracted_tables": all_tables
        }

    except Exception as e:
        print(f"❌ Error en parsing: {e}")
        return {"error": f"Error al leer el PDF: {str(e)}"}
    
    finally:
        # Limpieza: Borrar archivo temporal
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

def summarize_node(state: AgentState) -> AgentState:
    """
    NODO 2: Inteligencia / Resumen.
    Toma el texto extraído y utiliza un LLM (GPT-4o) para generar insights.
    """
    print("--- 🧠 NODE: AI Summarization ---")
    
    if state.get("error"):
        return state

    text = state.get("extracted_text", "")
    if not text:
        return {"summary": "No se pudo extraer texto suficiente para resumir."}

    # Recortar texto si es excesivamente largo para evitar errores de límite de tokens
    # (Una implementación más robusta usaría map-reduce o chunking de LangChain)
    text_preview = text[:25000] 

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Contexto adicional si viene de los metadatos
        filename = state.get("metadata", {}).get("filename", "Documento")

        prompt = f"""
        Actúa como un analista experto de operaciones. Analiza el siguiente texto extraído de un documento PDF llamado '{filename}'.
        
        Tu tarea:
        1. Generar un resumen ejecutivo conciso.
        2. Identificar los puntos clave, fechas importantes o datos monetarios si existen.
        3. Si hay tablas mencionadas en el texto, resalta su relevancia.

        Texto del Documento:
        {text_preview}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente útil y preciso para análisis de documentos corporativos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        
        # Actualizamos el estado con el resumen final
        return {"summary": summary}

    except Exception as e:
        print(f"❌ Error en LLM: {e}")
        return {"error": f"Error al contactar OpenAI: {str(e)}"}

# --- 3. Construcción del Grafo ---

# Inicializar el grafo con nuestro esquema de estado
workflow = StateGraph(AgentState)

# Añadir los nodos
workflow.add_node("parse_pdf", parse_pdf_node)
workflow.add_node("summarize", summarize_node)

# Definir las aristas (el flujo)
# Inicio -> Parsear -> Resumir -> Fin
workflow.set_entry_point("parse_pdf")
workflow.add_edge("parse_pdf", "summarize")
workflow.add_edge("summarize", END)

# Compilar el grafo para hacerlo ejecutable
app = workflow.compile()

# --- 4. Función Pública de Ejecución (Wrapper) ---

async def run_extraction(file_bytes: bytes, metadata: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Esta es la función principal que llamarán tanto la API como Streamlit.
    Se encarga de inicializar el estado y disparar el grafo.
    """
    # Estado inicial vacío
    initial_state = {
        "file_bytes": file_bytes,
        "metadata": metadata,
        "extracted_text": "",
        "extracted_tables": [],
        "summary": "",
        "error": None
    }
    
    # Ejecutar el grafo de forma asíncrona
    # LangGraph maneja el flujo entre nodos
    final_state = await app.ainvoke(initial_state)
    
    return final_state