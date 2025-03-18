import sys
import os
import tempfile
import json
import streamlit as st

# Ensure src directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extraction.contract_extractor import extract_and_clean_pdf
from src.extraction.extract_and_parse import structure_contract_sections
from src.llm.llm_query_handler import run_llm_task

# ---------------------- UI SETUP ----------------------
st.set_page_config(page_title="OpsBot Lite", layout="wide")
st.markdown("<h1 style='font-size: 36px;'>📑 OpsBot Lite</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; color: gray;'>Contract Intelligence Assistant for Internal Use</p>", unsafe_allow_html=True)

st.markdown("""
<hr style='margin-top: -15px; margin-bottom: 20px; border: 1px solid #e6e6e6;' />
""", unsafe_allow_html=True)

st.markdown("""
Upload a PDF contract and select an analysis task below to:
- Extract and organize contract fields
- Run LLM-powered insights (summary, risk flags, compliance checks)
""")

# ---------------------- USER INPUTS ----------------------
st.markdown("### 📥 Upload & Task Selection")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])

with col2:
    task_options = {
        "📌 Executive Summary": "summary",
        "⚠️ Highlight Potential Risks": "highlight_risks",
        "🚨 Identify Missing/Incomplete Fields": "missing_fields"
    }
    selected_label = st.selectbox("Select LLM Analysis Task", list(task_options.keys()))
    task_key = task_options[selected_label]

# ---------------------- MAIN PROCESS FLOW ----------------------
if uploaded_file:
    with st.spinner("🔍 Processing contract..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        raw = extract_and_clean_pdf(temp_path)
        structured = structure_contract_sections(raw["clean_text"])

    st.markdown("### 📂 Extracted Contract Sections")
    for section, content in structured.items():
        with st.expander(f"📄 {section.replace('_', ' ').title()}"):
            st.markdown(content if content else "*[Not Found]*")

    # ---------------------- LLM ANALYSIS ----------------------
    st.markdown("### 🤖 LLM-Generated Insights")
    with st.spinner(f"Generating {selected_label.lower()}..."):
        result = run_llm_task(structured, task=task_key)

    st.success("LLM analysis complete.")
    st.markdown(result if result else "*⚠️ LLM response could not be generated.*")

    # ---------------------- DOWNLOAD SECTION ----------------------
    st.markdown("### 📤 Export Results")

    st.download_button(
        label="📄 Download Result (.txt)",
        data=result,
        file_name=f"{uploaded_file.name}_llm_{task_key}.txt",
        mime="text/plain"
    )

    result_json = json.dumps({
        "structured_fields": structured,
        "llm_result": result
    }, indent=2)

    st.download_button(
        label="📁 Download Full Output (.json)",
        data=result_json,
        file_name=f"{uploaded_file.name}_llm_{task_key}.json",
        mime="application/json"
    )

# ---------------------- FOOTER ----------------------
st.markdown("<hr style='margin-top: 30px; border: 1px solid #e6e6e6;' />", unsafe_allow_html=True)
st.caption("🚀 Built by Miray Ozcan · Powered by OpenAI · Internal Demo for Proscia Product Operations Team")