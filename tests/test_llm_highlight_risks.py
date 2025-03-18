from dotenv import load_dotenv
import os
from openai import OpenAI
from src.extraction.extract_and_parse import structure_contract_sections
from src.extraction.contract_extractor import extract_and_clean_pdf

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def highlight_risks(contract_data: dict) -> str:
    prompt = f"""
You are a risk analyst reviewing a contract. Based on the contract fields below, highlight any risks, ambiguities, or potential bottlenecks that should be flagged for further review.

Here is the structured contract data:

### PROJECT_OVERVIEW:
{contract_data.get('project_overview', '[Not Provided]')}

### TIMELINE:
{contract_data.get('timeline', '[Not Provided]')}

### DELIVERABLES:
{contract_data.get('deliverables', '[Not Provided]')}

### TECHNICAL_NOTES:
{contract_data.get('technical_notes', '[Not Provided]')}

### PAYMENT_TERMS:
{contract_data.get('payment_terms', '[Not Provided]')}
"""

    print("\n📝 Prompt Sent to LLM:\n", prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert contract analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        print("\n🤖 LLM Response:\n", response.choices[0].message.content)
    except Exception as e:
        print("\n❌ LLM Query Failed:\n", e)

if __name__ == "__main__":
    pdf_path = "mock_data/mock_contract_2.pdf"
    extracted = extract_and_clean_pdf(pdf_path)
    structured = structure_contract_sections(extracted["clean_text"])
    highlight_risks(structured)