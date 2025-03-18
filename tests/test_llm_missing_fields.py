from src.extraction.extract_and_parse import structure_contract_sections
from src.extraction.contract_extractor import extract_and_clean_pdf
from src.llm.llm_query_handler import run_llm_task

def test_missing_fields():
    raw = extract_and_clean_pdf("mock_data/mock_contract_2.pdf")
    structured = structure_contract_sections(raw["clean_text"])
    run_llm_task(structured, task="missing_fields")

if __name__ == "__main__":
    test_missing_fields()