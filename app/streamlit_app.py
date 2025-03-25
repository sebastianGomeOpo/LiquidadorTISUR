import streamlit as st
from PIL import Image
from io import BytesIO
import pdfplumber
import tempfile
import os
from app.pdf_parser import extract_text_by_page, extract_tables_by_page

# Page config and title
st.set_page_config(page_title="PDF Extractor", page_icon="🔧", layout="wide")
st.title("📄 PDF Table & Text Extractor using pdfplumber")

# File upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    # Try extracting text and tables
    try:
        text_by_page = extract_text_by_page(pdf_path)
        tables_by_page = extract_tables_by_page(pdf_path)
    except Exception as e:
        st.error(f"❌ Failed to process PDF: {e}\n\nTry re-saving the file using a PDF viewer like Chrome or Preview.")
        st.stop()

    all_pages = list(text_by_page.keys())
    selected_page = st.selectbox("📑 Select a page to view", all_pages)

    # 🔽 Collapsible Extracted Text
    with st.expander("🧠 Extracted Text", expanded=False):
        st.text(text_by_page[selected_page])

    # 🔽 Collapsible Extracted Tables
    with st.expander("📊 Extracted Tables", expanded=False):
        if selected_page in tables_by_page:
            for i, df in enumerate(tables_by_page[selected_page]):
                st.markdown(f"#### 📎 Table {i+1}")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"⬇️ Download Table {i+1} (CSV)",
                    data=csv,
                    file_name=f"{selected_page}_table{i+1}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No tables found on this page.")

    # 🔍 Optional table debug image viewer
    if st.checkbox("🔍 Generate table debug images (for dev)?"):
        st.subheader("🖼️ Table Detection Debug View")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    im = page.to_image(resolution=150)
                    debug_im = im.debug_tablefinder(table_settings={
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                        "join_tolerance": 3,
                        "edge_min_length": 3,
                        "intersection_tolerance": 3
                    })

                    img_bytes = BytesIO()
                    debug_im.save(img_bytes, format="PNG")
                    img_bytes.seek(0)
                    st.image(img_bytes, caption=f"🧩 Table Debug — Page {i+1}")
                    st.markdown("---")
        except Exception as e:
            st.error(f"⚠️ Could not generate debug images: {e}")