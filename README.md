# OpsBot Lite: Structured Insights from Unstructured Chaos

Welcome to **OpsBot Lite**, a lightweight proof-of-concept (PoC) tool designed to tackle a key internal pain point surfaced during my Proscia Product Operations interview: **unstructured, scattered, and siloed internal data that makes strategic decision-making slow and inefficient.**

This project was inspired by a conversation with Proscia’s Product Operations team about the growing need to extract structured insights from diverse sources like **CRM notes, PDF contracts, and internal documentation**, and to consolidate these insights into a **queryable, presentable, and role-specific format.**

## Problem Statement
Proscia is a high-growth digital pathology leader—growing fast, scaling globally, and adding complexity across internal systems. Yet, internal data often:
- Exists across disparate formats (PDFs, CRMs, notes)
- Is manually entered and error-prone
- Is unstructured and hard to query
- Lives in silos across departments

This limits Proscia’s ability to **act quickly and make data-driven decisions at scale**.

## 💡 Solution: OpsBot Lite
**OpsBot Lite** is a **LLM-powered internal tooling pipeline** that:
1. Ingests unstructured documents (e.g., PDF contracts, CRM exports)
2. Extracts and standardizes key fields using GPT-based prompt engineering
3. Stores results in a structured, queryable SQLite database or CSV format
4. (Optional) Visualizes extracted insights through a lightweight dashboard

This prototype showcases **how an LLM-powered automation script can reduce hours of manual data wrangling into seconds—freeing Proscia teams to focus on what matters: delivering life-changing technology faster.**

## 🔧 Architecture Overview
```
           +---------------------+
           | Upload Documents   |
           | (.pdf / .txt / .csv)|
           +---------+----------+
                     |
             +-------v--------+
             | LLM Extraction |
             | (GPT + Prompts)|
             +-------+--------+
                     |
           +---------v-----------+
           | Normalize & Clean   |
           +---------+-----------+
                     |
         +-----------v-----------+
         | Store to SQLite/CSV   |
         +-----------+-----------+
                     |
       +-------------v---------------+
       | (Optional) Streamlit View   |
       +-----------------------------+
```

## 📦 Sample Output Fields
- Customer Name
- Product Purchased (e.g., Concentriq AP-Dx, Embeddings)
- Contract Start Date / Value
- Configuration Details
- Custom Features
- Internal Stakeholders

## 📌 Tech Stack
- Python
- LangChain or OpenAI SDK
- PyMuPDF/pdfplumber (PDF Parsing)
- SQLite or CSV
- Streamlit (Optional Visualization Layer)

## 🚀 Why This Matters for Proscia
This project reflects:
- **Product Operations Mindset**: Prioritizing pain points, scoping MVPs, and building fast
- **Startup Execution Grit**: Building scrappy solutions with high impact potential
- **AI-First Thinking**: Leveraging LLMs for internal efficiency
- **Cross-Functional Awareness**: Designed with executives, product managers, and engineers in mind

## 🧩 Next Steps
- [ ] Create simulated CRM and contract files
- [ ] Build LLM extraction pipeline
- [ ] Normalize and structure output
- [ ] (Optional) Add Streamlit viewer

## ✨ Final Note
This is a small step toward a bigger opportunity: **internal AI-powered tooling that saves time, reduces manual error, and amplifies decision velocity.**

Thank you again for the inspiration, and I’m excited to show how I think about building for impact—before Day One.

