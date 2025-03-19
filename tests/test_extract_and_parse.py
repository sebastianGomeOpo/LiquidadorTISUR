from src.extraction.contract_extractor import extract_and_clean_pdf
from src.extraction.extract_and_parse import structure_contract_sections

def test_parse_contract():
    pdf_path = "mock_data/mock_contract_1.pdf"
    raw_text = extract_and_clean_pdf(pdf_path)
    structured = structure_contract_sections(raw_text["clean_text"])

    print("\n🔍 Structured Contract Fields:")
    for section, content in structured.items():
        print(f"\n--- {section.upper()} ---\n{content if content else '[Not Found]'}")


if __name__ == "__main__":
    test_parse_contract()