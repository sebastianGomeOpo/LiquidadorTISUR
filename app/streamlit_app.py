import streamlit as st
import tempfile
import os
import openai
from dotenv import load_dotenv
from app.pdf_parser import (
    extract_text_single_page,
    extract_tables_single_page,
    extract_total_pages,
    save_debug_image_single_page,
    summarize_pdf,
    summarize_page
)

# === Load environment ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Page config ===
st.set_page_config(page_title="PDF Extractor", page_icon="🔧", layout="wide")
st.title("📄 PDF Table & Text Extractor")

# === File Uploader ===
uploaded_file = st.file_uploader("📎 Upload a PDF file", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.session_state["pdf_path"] = pdf_path

    # === Total Pages ===
    try:
        total_pages = extract_total_pages(pdf_path)
    except Exception as e:
        st.error(f"❌ Failed to read PDF: {e}")
        st.stop()

    # === Extract All Text Once ===
    if "full_text_by_page" not in st.session_state:
        st.session_state["full_text_by_page"] = {
            f"Page {i+1}": extract_text_single_page(pdf_path, i)
            for i in range(total_pages)
        }

    # === Summarize PDF Button ===
    if "global_summary" not in st.session_state:
        if st.button("🧠 Summarize Full PDF"):
            with st.spinner("Summarizing the entire PDF..."):
                st.session_state["global_summary"] = summarize_pdf(st.session_state["full_text_by_page"])

    # === Show Global Summary ===
    if "global_summary" in st.session_state:
        with st.expander("🧠 PDF Overview Summary", expanded=True):
            st.success(st.session_state["global_summary"])

    # === Page Selection ===
    page_options = [f"Page {i}" for i in range(1, total_pages + 1)]
    selected_page_label = st.selectbox("📑 Select a page to view", page_options)
    selected_page_idx = int(selected_page_label.split(" ")[1])
    page_label = f"Page {selected_page_idx}"
    page_text = st.session_state["full_text_by_page"][page_label]

    # === Track Page Switching ===
    if "last_selected_page" not in st.session_state:
        st.session_state.last_selected_page = selected_page_idx

    if selected_page_idx != st.session_state.last_selected_page:
        st.session_state.expand_text_section = False  # Collapse when switching
        st.session_state.last_selected_page = selected_page_idx

    if "expand_text_section" not in st.session_state:
        st.session_state.expand_text_section = False

    # === Extract Tables ===
    try:
        tables, strategy = extract_tables_single_page(pdf_path, selected_page_idx - 1)
    except Exception as e:
        st.error(f"❌ Error extracting content: {e}")
        st.stop()

    # === Text Section with Summary ===
    with st.expander("🧠 Extracted Text", expanded=st.session_state.expand_text_section):
        col1, col2 = st.columns([1, 6])
        with col1:
            summarize_triggered = st.button("📝 Summarize This Page", key=f"summary-btn-{selected_page_idx}")
        with col2:
            pass

        if summarize_triggered:
            if "global_summary" not in st.session_state:
                st.warning("Please summarize the full PDF first.")
            else:
                with st.spinner("Summarizing this page..."):
                    summary = summarize_page(page_text, context_summary=st.session_state["global_summary"])
                    st.session_state[f"page_{selected_page_idx}_summary"] = summary
                    st.session_state.expand_text_section = True  # Keep open after rerun

        if f"page_{selected_page_idx}_summary" in st.session_state:
            st.markdown("**🔍 Page Summary:**")
            st.info(st.session_state[f"page_{selected_page_idx}_summary"])

        st.text(page_text)

    # === Tables Section ===
    with st.expander("📊 Extracted Tables", expanded=False):
        strategy_color = {
            "lines": "🟢",
            "none": "🔴",
            "error": "❌",
            "unknown": "⚪️"
        }.get(strategy, "⚪️")

        st.markdown(f"**Strategy used:** {strategy_color} `{strategy}`")

        if tables and strategy != "none":
            for i, df in enumerate(tables):
                st.markdown(f"#### 📎 Table {i+1}")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"⬇️ Download Table {i+1} (CSV)",
                    data=csv,
                    file_name=f"{page_label}_table{i+1}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No tables found on this page.")

    # === Optional Debug Image ===
    if st.checkbox("🔍 Generate table preview image for selected page?"):
        st.subheader(f"🖼️ Table Detection Preview — {page_label}")
        try:
            img_bytes = save_debug_image_single_page(pdf_path, selected_page_idx - 1)
            st.image(img_bytes, caption=f"🧩 Table Preview — {page_label}")
        except Exception as e:
            st.error(f"⚠️ Could not generate preview image: {e}")