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

def extract_text_by_page(pdf_path):
    text_pages = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            text_pages[f"Page {i+1}"] = text or "[No text detected]"
    return text_pages


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
    
    # Allow tables even if they have lots of short cells
    if non_empty_cells / total_cells < 0.4:
        return False

    return True


def extract_tables_with_line_strategy(pdf_path, verbose=False):
    tables_by_page = {}
    strategy_by_page = {}

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_label = f"Page {i+1}"
            try:
                raw_tables = page.extract_tables(table_settings=DEFAULT_TABLE_SETTINGS)
                valid_tables = [t for t in raw_tables if is_valid_table(t)]

                if valid_tables:
                    tables_by_page[page_label] = [pd.DataFrame(t) for t in valid_tables]
                    strategy_by_page[page_label] = "lines"
                else:
                    strategy_by_page[page_label] = "none"

            except Exception as e:
                if verbose:
                    print(f"⚠️ Error extracting tables from {page_label}: {e}")
                strategy_by_page[page_label] = "error"

    return tables_by_page, strategy_by_page


def extract_tables_safely(pdf_path, verbose=False):
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables(table_settings=DEFAULT_TABLE_SETTINGS)
                valid_tables = [t for t in tables if is_valid_table(t)]
                if not valid_tables:
                    print(f"Page {i+1}: No valid tables found.")
                    continue
                for t_idx, table in enumerate(valid_tables):
                    df = pd.DataFrame(table)
                    print(f"\nPage {i+1} - Table {t_idx+1}")
                    print(df)
                    if verbose:
                        print(df.to_markdown())
            except Exception as e:
                print(f"❌ Failed to extract tables from Page {i+1}: {e}")


def save_debug_images(pdf_path, output_dir="debug_tables", resolution=150, table_settings=None):
    os.makedirs(output_dir, exist_ok=True)
    table_settings = table_settings or DEFAULT_TABLE_SETTINGS

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                im = page.to_image(resolution=resolution)
                debug_im = im.debug_tablefinder(table_settings=table_settings)

                # 🔍 Optional: Draw detected rectangles in blue for better visual inspection
                debug_im.draw_rects(page.rects, stroke="blue", stroke_width=1)

                image_path = os.path.join(output_dir, f"debug_page_{i+1}.png")
                debug_im.save(image_path)
            except Exception as e:
                print(f"⚠️ Couldn't generate debug image for Page {i+1}: {e}")