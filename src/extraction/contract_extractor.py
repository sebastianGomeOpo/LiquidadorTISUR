import os
import fitz  # PyMuPDF
from typing import List, Dict


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a PDF using PyMuPDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    doc.close()
    return full_text


def clean_extracted_text(raw_text: str) -> str:
    """Cleans up raw extracted text (removes line breaks, normalizes whitespace, etc)."""
    text = raw_text.replace('\n', ' ').replace('\xa0', ' ')
    text = ' '.join(text.split())  # Normalize excessive whitespace
    return text


def extract_and_clean_pdf(pdf_path: str) -> Dict:
    """Main function to extract and clean PDF text."""
    raw_text = extract_text_from_pdf(pdf_path)
    clean_text = clean_extracted_text(raw_text)
    return {
        "filename": os.path.basename(pdf_path),
        "raw_text": raw_text,
        "clean_text": clean_text
    }