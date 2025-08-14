import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import re
import zipfile
import io

st.set_page_config(page_title="Invoice Splitter", page_icon="📄", layout="centered")
st.title("📄 Invoice Splitter by Invoice Number")
st.write("Upload a PDF containing invoices and split them into individual files named by invoice number.")

uploaded_file = st.file_uploader("Upload your PDF invoice file", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    invoice_pages = {}
    current_invoice = None

    # Loop over each page and detect invoice number
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "Invoice No." in line:
                if i + 1 < len(lines):
                    possible_line = lines[i + 1]
                    match = re.search(r"\b(\d{5,})\b", possible_line)
                    if match:
                        current_invoice = match.group(1)
                        invoice_pages[current_invoice] = []
                        break
        if current_invoice:
            invoice_pages[current_invoice].append(page_num)

    if invoice_pages:
        st.success(f"Found {len(invoice_pages)} invoices: {', '.join(invoice_pages.keys())}")

        # Create a zip with all split PDFs
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for invoice_num, pages in invoice_pages.items():
                writer = PdfWriter()
                for p in pages:
                    writer.add_page(reader.pages[p])
                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                zipf.writestr(f"{invoice_num}.pdf", pdf_bytes.getvalue())

        zip_buffer.seek(0)
        st.download_button(
            label="⬇️ Download All Invoices (ZIP)",
            data=zip_buffer,
            file_name="split_invoices.zip",
            mime="application/zip"
        )
    else:
        st.error("No invoice numbers found. Please check your PDF format.")
