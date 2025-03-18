import re

def structure_contract_sections(clean_text: str) -> dict:
    sections = {}

    # Improved regex patterns with alternative section headers
    patterns = {
        "project_overview": r'(?i)(project overview|scope of services)[:\-–]?\s*(.*?)(?=\b(timeline|deployment plan|deliverables|key outputs|technical infrastructure|technical notes|support|signature|payment terms|termination)\b)',
        "timeline": r'(?i)(timeline|deployment plan|implementation schedule)[:\-–]?\s*(.*?)(?=\b(deliverables|key outputs|technical infrastructure|technical notes|support|signature|payment terms|termination)\b)',
        "deliverables": r'(?i)(deliverables|scope of work|key outputs)[:\-–]?\s*(.*?)(?=\b(technical infrastructure|technical notes|support|signature|payment terms|termination)\b)',
        "technical_notes": r'(?i)(technical infrastructure|technical notes)[:\-–]?\s*(.*?)(?=\b(support|support agreement|signature|payment terms|termination)\b)',
        "payment_terms": r'(?i)(payment terms)[:\-–]?\s*(.*?)(?=\b(termination|signature|support agreement|support|technical infrastructure|technical notes)\b)',
    }

    for section, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.IGNORECASE | re.DOTALL)
        sections[section] = match.group(2).strip() if match else None

    # Optional cleanup logic: clip PAYMENT_TERMS if it overflowed into TECHNICAL_NOTES
    if sections["payment_terms"] and "Technical Infrastructure" in sections["payment_terms"]:
        sections["payment_terms"] = sections["payment_terms"].split("Technical Infrastructure")[0].strip()

    return sections