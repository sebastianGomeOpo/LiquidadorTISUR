from src.llm.llm_query_handler import build_prompt, query_llm
from src.extraction.extract_and_parse import structure_contract_sections
from src.extraction.contract_extractor import extract_and_clean_pdf

def test_llm_summarization():
    contract_path = "mock_data/mock_contract_2.pdf"
    contract = extract_and_clean_pdf(contract_path)
    structured = structure_contract_sections(contract["clean_text"])
    
    prompt = build_prompt(structured, task="summarize")
    print("\n📝 Prompt Sent to LLM:\n", prompt[:1000])  # Print first 1000 chars
    response = query_llm(prompt)
    print("\n🤖 LLM Response:\n", response)

if __name__ == "__main__":
    test_llm_summarization()