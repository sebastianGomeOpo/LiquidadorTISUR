from src.extraction.contract_extractor import extract_and_clean_pdf
import os

def test_pdf_extraction():
    mock_dir = "mock_data"
    files = [f for f in os.listdir(mock_dir) if f.endswith(".pdf")]

    for file in files:
        print(f"\n--- Extracting from: {file} ---")
        pdf_path = os.path.join(mock_dir, file)
        result = extract_and_clean_pdf(pdf_path)

        print("Cleaned Text Sample:\n")
        print(result["clean_text"][:800])  # Preview first 800 chars

if __name__ == "__main__":
    test_pdf_extraction()