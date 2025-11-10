import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from utils.qa_pipeline import QAPipeline
from utils.report_generator import dataframe_to_csv_bytes, dataframe_to_pdf_bytes

load_dotenv()

st.set_page_config(page_title='Business News AI Analyst', page_icon='🧠', layout='wide')
st.title('🧠 Business News AI Analyst')

urls_input = st.text_area('Paste News URLs (one per line):', height=150)
qs_input = st.text_area('Enter Questions (one per line):', height=150)

if st.button('Generate Report'):
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    qs = [q.strip() for q in qs_input.splitlines() if q.strip()]
    if not urls or not qs:
        st.error('Please add both URLs and questions.')
    else:
        try:
            pipe = QAPipeline()
            pipe.build_embeddings(urls)
            results = []
            for q in qs:
                ans, used = pipe.answer(q)
                results.append({'Question': q, 'Answer': ans, 'Sources': ' | '.join(used)})
            df = pd.DataFrame(results)
            st.dataframe(df)
            st.download_button('📄 Download CSV', dataframe_to_csv_bytes(df), 'business_ai_report.csv', 'text/csv')
            st.download_button('📘 Download PDF', dataframe_to_pdf_bytes(df), 'business_ai_report.pdf', 'application/pdf')
        except Exception as e:
            st.error(f'Error: {e}')
