import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import re
from io import BytesIO

st.title("Crawford Invoice Splitter")
st.write("Upload a PDF, and this will split it into separate invoices based on the invoice number.")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    invoice_pattern = re.compile(r"INVOICE NUMBER\s+([A-Z0-9]+\.\d{3})")

    invoices = {}
    current_invoice = None

    for page in reader.pages:
        text = page.extract_text()
        if text:
            match = invoice_pattern.search(text)
            if match:
                current_invoice = match.group(1)
                if current_invoice not in invoices:
                    invoices[current_invoice] = PdfWriter()
            if current_invoice:
                invoices[current_invoice].add_page(page)

    st.success(f"Found {len(invoices)} invoices.")

    for invoice_num, writer in invoices.items():
        pdf_bytes = BytesIO()
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)
        st.download_button(
            label=f"Download {invoice_num}.pdf",
            data=pdf_bytes,
            file_name=f"{invoice_num}.pdf",
            mime="application/pdf"
        )
