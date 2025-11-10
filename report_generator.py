import io
import pandas as pd
from fpdf import FPDF

def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')

def dataframe_to_pdf_bytes(df: pd.DataFrame, title='Business AI Report') -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font('Arial', '', 11)
    for _, row in df.iterrows():
        pdf.multi_cell(0, 8, f"Q: {row['Question']}")
        pdf.multi_cell(0, 8, f"A: {row['Answer']}")
        pdf.multi_cell(0, 8, f"Sources: {row['Sources']}")
        pdf.ln(5)
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
