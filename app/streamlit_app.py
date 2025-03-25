import streamlit as st
from io import BytesIO
import tempfile
import os
from app.pdf_parser import (
    extract_text_single_page,
    extract_tables_single_page,
    extract_total_pages,
    save_debug_image_single_page,
    DEFAULT_TABLE_SETTINGS
)

# Page config and title
st.set_page_config(page_title="PDF Extractor", page_icon="🔧", layout="wide")
st.title("📄 PDF Table & Text Extractor")

# File upload
uploaded_file = st.file_uploader("📎 Upload a PDF file", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    # Get total pages without reading all
    try:
        total_pages = extract_total_pages(pdf_path)
    except Exception as e:
        st.error(f"❌ Failed to read PDF: {e}")
        st.stop()

    page_options = [f"Page {i}" for i in range(1, total_pages + 1)]
    selected_page_label = st.selectbox("📑 Select a page to view", page_options)
    selected_page_idx = int(selected_page_label.split(" ")[1])
    page_label = f"Page {selected_page_idx}"

    # Extract only selected page's content
    try:
        text = extract_text_single_page(pdf_path, selected_page_idx - 1)
        tables, strategy = extract_tables_single_page(pdf_path, selected_page_idx - 1)
    except Exception as e:
        st.error(f"❌ Error extracting content: {e}")
        st.stop()

    # 🔽 Collapsible Extracted Text
    with st.expander("🧠 Extracted Text", expanded=False):
        st.text(text)

    # 🔽 Collapsible Extracted Tables
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

    # 🔍 Debug image generator
    if st.checkbox("🔍 Generate an image for selected page to verify table detection?"):
        st.subheader(f"🖼️ Table Detection Preview — {page_label}")

        try:
            img_bytes = save_debug_image_single_page(pdf_path, selected_page_idx - 1)
            st.markdown(f"**🟢 Line-based — {page_label}**")
            st.image(img_bytes, caption=f"🧩 Table Debug — {page_label}")
        except Exception as e:
            st.error(f"⚠️ Could not generate debug image: {e}")