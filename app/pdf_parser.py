import os
import pdfplumber
import pandas as pd

# Default table settings — enhanced for line-based tables using rectangles
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


def is_valid_table(table):
    if not table or not isinstance(table, list) or len(table) < 2:
        return False

    row_lengths = [len(row) for row in table]
    if max(row_lengths, default=0) < 2:
        return False

    total_cells = sum(len(row) for row in table)
    non_empty_cells = sum(1 for row in table for cell in row if cell and cell.strip())

    if total_cells == 0:
        return False

    if non_empty_cells / total_cells < 0.4:
        return False

    return True


def extract_text_single_page(pdf_path, page_number):
    """
    Extracts plain text from a single page.
    Returns: str
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        return page.extract_text() or "[No text detected]"


def extract_tables_single_page(pdf_path, page_number, verbose=False):
    """
    Extracts tables from a single page.
    Returns: (List[pd.DataFrame], strategy: str)
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_number]
            raw_tables = page.extract_tables(table_settings=DEFAULT_TABLE_SETTINGS)
            valid_tables = [t for t in raw_tables if is_valid_table(t)]
            dfs = [pd.DataFrame(t) for t in valid_tables]
            strategy = "lines" if dfs else "none"
            return dfs, strategy
    except Exception as e:
        if verbose:
            print(f"⚠️ Error extracting tables from page {page_number + 1}: {e}")
        return [], "error"


def extract_total_pages(pdf_path):
    """
    Returns total number of pages in the PDF.
    """
    with pdfplumber.open(pdf_path) as pdf:
        return len(pdf.pages)


def save_debug_image_single_page(pdf_path, page_number, resolution=100, table_settings=None):
    """
    Generates and returns a debug image for table detection on a single page.
    Returns: BytesIO image stream
    """
    from io import BytesIO

    table_settings = table_settings or DEFAULT_TABLE_SETTINGS

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        im = page.to_image(resolution=resolution)
        debug_im = im.debug_tablefinder(table_settings=table_settings)

        # Draw rectangles for visual assistance
        debug_im.draw_rects(page.rects, stroke="blue", stroke_width=1)

        img_bytes = BytesIO()
        debug_im.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return img_bytes