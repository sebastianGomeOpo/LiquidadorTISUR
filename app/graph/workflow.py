import os
import tempfile
from typing import TypedDict, List, Any, Optional, Dict
from langgraph.graph import StateGraph, END

# --- IMPORT NUEVO: Herramienta de Landing AI ---
from app.tools.landing_ade import extract_markdown_with_landing_ai

# Cliente de OpenAI para la extracción de datos
from openai import OpenAI

# --- 1. Definición del Estado del Agente ---
class AgentState(TypedDict):
    """
    Define la estructura de datos que viaja a través del grafo.
    """
    file_bytes: bytes          # Input: El archivo PDF crudo
    metadata: Dict[str, Any]   # Input: Datos extra (nombre archivo, etc.)
    
    extracted_text: str        # Output intermedio: Markdown generado por Landing AI
    extracted_tables: List[Any]# Output intermedio: (Vacio con Landing AI, ya que las tablas están en el markdown)
    
    summary: str               # Output final: JSON con los datos de TISUR
    error: Optional[str]       # Manejo de errores

# --- 2. Definición de Nodos (Pasos del Proceso) ---

def parse_pdf_node(state: AgentState) -> AgentState:
    """
    NODO 1: Ingesta y Extracción con Landing AI.
    Convierte el PDF a Markdown de alta fidelidad.
    """
    print("--- 🔄 NODE: Parsing PDF with Landing AI ---")
    
    # Si ya hay un error previo, saltamos
    if state.get("error"):
        return state

    tmp_path = None
    try:
        # 1. Guardar bytes en archivo temporal (Landing AI requiere un path de archivo)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(state["file_bytes"])
            tmp_path = tmp.name

        # 2. Ejecutar extracción usando la nueva herramienta
        markdown_text = extract_markdown_with_landing_ai(tmp_path)
        
        print(f"   ✅ Extracción completada. Longitud: {len(markdown_text)} caracteres.")

        # Nota: Landing AI integra las tablas visualmente dentro del texto Markdown.
        # Dejamos extracted_tables vacío porque el LLM leerá las tablas desde el texto.
        
        return {
            "extracted_text": markdown_text,
            "extracted_tables": [] 
        }

    except Exception as e:
        print(f"❌ Error en parsing: {e}")
        return {"error": f"Error al procesar el PDF: {str(e)}"}
    
    finally:
        # Limpieza: Borrar archivo temporal
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

def summarize_node(state: AgentState) -> AgentState:
    """
    NODO 2: Extracción de Datos Estructurados (TISUR).
    Analiza el Markdown y extrae los campos específicos solicitados.
    """
    print("--- 🧠 NODE: AI Data Extraction ---")
    
    if state.get("error"):
        return state

    text = state.get("extracted_text", "")
    if not text or "Error" in text[:50]:
        return {"summary": "No se pudo extraer texto válido para procesar."}

    # Recortar texto si es excesivamente largo (Landing AI puede generar mucho texto)
    # GPT-4o tiene una ventana grande, pero por seguridad y costo limitamos.
    text_preview = text[:50000] 

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        filename = state.get("metadata", {}).get("filename", "Documento")

        # --- PROMPT ESPECÍFICO PARA DATOS TISUR ---
        prompt = f"""
        Actúa como un experto en logística aduanera y liquidaciones portuarias.
        Analiza el siguiente documento que ha sido convertido a formato MARKDOWN (preservando tablas y estructura).
        
        Nombre del archivo: '{filename}'
        
        Tu OBJETIVO es extraer EXCLUSIVAMENTE la siguiente información y devolverla en formato JSON válido.
        Busca en encabezados, cuerpos de texto y tablas.
        
        CAMPOS A EXTRAER:
        1. "Nombre de la nave": (Busca: MN, M/N, Vessel, Nave, Vapor)
        2. "Nro de Nota de embarque": (Busca: B/L, Bill of Lading, Nota de Embarque, Conocimiento de Embarque)
        3. "Nro de Lote": (Busca: Lote, Batch, Lot No)
        4. "Puerto de destino": (Busca: Puerto de Descarga, Port of Discharge, POD, Destino)
        5. "Tipo de carga": (Descripción de la mercancía, ej: Trigo, Maíz, Bobinas, Urea)
        6. "Cantidad total": (Busca el Peso Neto o Peso Bruto total manifestado, ej: 5000 MT, KGS)
        7. "Nro de DAM": (Declaración Aduanera de Mercancías, formato numérico de aduanas)

        REGLAS:
        - Si un dato no aparece en el documento, asigna el valor null.
        - Devuelve SOLO el objeto JSON. No incluyas bloques de código (```json) ni texto adicional.
        - Si hay múltiples valores posibles (ej. varios lotes), intenta consolidarlos o tomar el principal.

        Documento (Markdown):
        {text_preview}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un motor de extracción de datos JSON preciso."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0 # Temperatura 0 para máxima precisión y determinismo
        )

        summary = response.choices[0].message.content.strip()
        
        # Limpieza básica por si el modelo devuelve markdown code blocks
        if summary.startswith("```json"):
            summary = summary.replace("```json", "").replace("```", "")
        
        return {"summary": summary}

    except Exception as e:
        print(f"❌ Error en LLM: {e}")
        return {"error": f"Error al contactar OpenAI: {str(e)}"}

# --- 3. Construcción del Grafo ---

workflow = StateGraph(AgentState)

# Añadir los nodos
workflow.add_node("parse_pdf", parse_pdf_node)
workflow.add_node("summarize", summarize_node)

# Definir las aristas
workflow.set_entry_point("parse_pdf")
workflow.add_edge("parse_pdf", "summarize")
workflow.add_edge("summarize", END)

# Compilar
app = workflow.compile()

# --- 4. Función Pública ---

async def run_extraction(file_bytes: bytes, metadata: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Función principal llamada por la API y Streamlit.
    """
    initial_state = {
        "file_bytes": file_bytes,
        "metadata": metadata,
        "extracted_text": "",
        "extracted_tables": [],
        "summary": "",
        "error": None
    }
    
    final_state = await app.ainvoke(initial_state)
    return final_state