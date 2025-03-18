import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_llm_task(structured_data: dict, task: str = "summary") -> str:
    task_prompts = {
        "summary": "You are an expert contract analyst. Based on the following contract fields, provide a concise 5-bullet-point summary for executive review.",
        "highlight_risks": "You are a risk analyst reviewing a contract. Based on the contract fields below, highlight any risks, ambiguities, or potential bottlenecks that should be flagged for further review.",
        "missing_fields": """You are a compliance reviewer. Review the contract fields below and identify any missing, vague, or inconsistent sections.
                             For each section, explicitly mention if it’s clearly provided, vague or incomplete, or missing entirely.
                             Then list any follow-up questions or additional information you would request from the contract author to resolve gaps."""
    }

    prompt = task_prompts.get(task, task_prompts["summary"])

    # Format structured data into the prompt
    formatted_sections = ""
    for section, content in structured_data.items():
        formatted_sections += f"\n### {section.upper()}:\n{content if content else '[Not Provided]'}\n"

    full_prompt = f"{prompt}\n\nHere is the structured contract data:\n{formatted_sections}"

    print("\n📝 Prompt Sent to LLM:\n", full_prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=500
        )

        reply = response.choices[0].message.content.strip()
        print("\n🤖 LLM Response:\n", reply)
        return reply

    except Exception as e:
        print("\n❌ LLM Query Failed:\n", e)
        return None