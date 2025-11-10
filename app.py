# ================================================
# 🧠 Business News AI Analyst - Streamlit App
# ================================================

import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from utils.qa_pipeline import QAPipeline
from utils.report_generator import dataframe_to_csv_bytes, dataframe_to_pdf_bytes

# ✅ Load environment variables (optional)
load_dotenv()

# ✅ Streamlit page configuration
st.set_page_config(
    page_title="Business News AI Analyst",
    page_icon="🧠",
    layout="wide"
)
# ===============================
# 🧠 Business News AI Analyst UI
# ===============================

st.title("🧠 Business News AI Analyst")
st.markdown("Get instant, AI-generated insights from recent financial and IPO news articles.")

# Instantiate the AI pipeline
qa = QAPipeline()

st.subheader("📥 Step 1: Enter News URLs")
urls_input = st.text_area("Paste news URLs (one per line):", height=150)

if st.button("Build Knowledge Base"):
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        with st.spinner("Extracting and embedding articles..."):
            try:
                qa.build_embeddings(urls)
                st.success("✅ Articles successfully processed!")
            except Exception as e:
                st.error(f"Error: {e}")

st.subheader("💬 Step 2: Ask Questions")
question = st.text_area("Enter your analysis questions:", height=120)

if st.button("Generate Insights"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing context and generating answers..."):
            try:
                answer, sources = qa.answer(question)
                st.markdown("### 🧩 AI Insight:")
                st.write(answer)
                st.markdown("**Sources:**")
                for s in sources:
                    st.markdown(f"- [{s}]({s})")
            except Exception as e:
                st.error(f"Error: {e}")
