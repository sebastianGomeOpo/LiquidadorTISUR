import pdfplumber
import pandas as pd
from typing import List, Union, Tuple, Any
from io import BytesIO

# === Configuración de Tablas ===
# Mantenemos la configuración probada para detección de líneas
DEFAULT_TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 4,
    "join_tolerance": 4,
    "edge_min_length": 5,
    "intersection_tolerance": 5,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
}

# === Funciones de Validación ===

def is_valid_table(table: List[List[str]]) -> bool:
    """
    Heurística para descartar tablas 'falsas' o vacías detectadas por pdfplumber.
    """
    if not table or not isinstance(table, list) or len(table) < 2:
        return False

    # Verificar que tenga dimensiones razonables
    row_lengths = [len(row) for row in table]
    if max(row_lengths, default=0) < 2:
        return False

    # Verificar densidad de datos (evitar tablas vacías)
    total_cells = sum(len(row) for row in table)
    non_empty_cells = sum(1 for row in table for cell in row if cell and str(cell).strip())

    if total_cells == 0 or (non_empty_cells / total_cells < 0.4):
        return False

    return True

# === Funciones de Extracción Pura ===

def extract_total_pages(pdf_input: Union[str, BytesIO]) -> int:
    """
    Abre el PDF y devuelve el número total de páginas.
    """
    with pdfplumber.open(pdf_input) as pdf:
        return len(pdf.pages)

def extract_text_single_page(pdf_input: Union[str, BytesIO], page_number: int) -> str:
    """
    Extrae el texto crudo de una página específica.
    """
    with pdfplumber.open(pdf_input) as pdf:
        # Validación de rango de página
        if page_number < 0 or page_number >= len(pdf.pages):
            return ""
            
        page = pdf.pages[page_number]
        return page.extract_text() or "[Sin texto detectable]"

def extract_tables_single_page(
    pdf_input: Union[str, BytesIO], 
    page_number: int
) -> Tuple[List[pd.DataFrame], str]:
    """
    Extrae tablas de una página y las convierte a DataFrames de Pandas.
    Devuelve: (Lista de DataFrames, Estrategia usada)
    """
    try:
        with pdfplumber.open(pdf_input) as pdf:
            if page_number < 0 or page_number >= len(pdf.pages):
                return [], "error"

            page = pdf.pages[page_number]
            
            # Extracción
            raw_tables = page.extract_tables(table_settings=DEFAULT_TABLE_SETTINGS)
            
            # Validación y Limpieza
            valid_tables = [t for t in raw_tables if is_valid_table(t)]
            dfs = [pd.DataFrame(t) for t in valid_tables]
            
            strategy = "lines" if dfs else "none"
            return dfs, strategy

    except Exception as e:
        print(f"⚠️ Error extrayendo tablas en página {page_number + 1}: {e}")
        return [], "error"

def save_debug_image_single_page(
    pdf_input: Union[str, BytesIO], 
    page_number: int, 
    resolution: int = 150
) -> BytesIO:
    """
    Genera una imagen de la página con las líneas de tabla detectadas dibujadas encima.
    Útil para depuración visual en la UI.
    """
    img_bytes = BytesIO()
    
    try:
        with pdfplumber.open(pdf_input) as pdf:
            if page_number < 0 or page_number >= len(pdf.pages):
                return None

            page = pdf.pages[page_number]
            # Renderizar página a imagen
            im = page.to_image(resolution=resolution)
            
            # Dibujar las tablas detectadas
            debug_im = im.debug_tablefinder(table_settings=DEFAULT_TABLE_SETTINGS)
            
            # Guardar en buffer de memoria
            debug_im.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return img_bytes

    except Exception as e:
        print(f"⚠️ Error generando imagen de debug: {e}")
        return None