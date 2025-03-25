import pdfplumber
import pandas as pd
import os

DEFAULT_TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "intersection_tolerance": 3
}

def extract_text_by_page(pdf_path):
    """
    Extract plain text from each page of the PDF.
    Returns: Dict[str, str] where key = Page label, value = extracted text
    """
    with pdfplumber.open(pdf_path) as pdf:
        return {
            f"Page {i+1}": page.extract_text() or "[No text detected]"
            for i, page in enumerate(pdf.pages)
        }


def extract_tables_by_page(pdf_path, table_settings=None):
    """
    Extract all tables from every page of the PDF using optional custom table_settings.
    Returns: Dict[str, List[pd.DataFrame]] where key = Page label
    """
    all_tables = {}
    table_settings = table_settings or DEFAULT_TABLE_SETTINGS

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            raw_tables = page.extract_tables(table_settings=table_settings)
            if raw_tables:
                dfs = [pd.DataFrame(table) for table in raw_tables if table]
                if dfs:
                    all_tables[f"Page {i+1}"] = dfs

    return all_tables

def save_debug_images(pdf_path, output_dir="debug_tables", resolution=150, table_settings=None):
    """
    Saves visual debug images of table detection for all pages in the PDF.
    """

    os.makedirs(output_dir, exist_ok=True)

    table_settings = table_settings or {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "join_tolerance": 3,
        "edge_min_length": 3,
        "intersection_tolerance": 3
    }

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            im = page.to_image(resolution=resolution)
            debug_im = im.debug_tablefinder(table_settings=table_settings)
            image_path = os.path.join(output_dir, f"debug_page_{i+1}.png")
            debug_im.save(image_path)