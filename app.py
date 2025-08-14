import streamlit as st
import fitz
import re
from io import BytesIO

# Position-based invoice number extractor
def extract_invoice_number_by_position(page):
    # Coordinates from example "1307919A"
    ref_x1, ref_x2 = 20, 100
    ref_y1, ref_y2 = 260, 280
    words = page.get_text("words")
    for w in words:
        x0, y0, x1, y1, word, *_ = w
        if ref_x1 <= x0 <= ref_x2 and ref_y1 <= y0 <= ref_y2:
            if re.match(r"^\d{7}[A-Z]?$", word):
                return word
    return None

# UI
st.title("📄 Johnstone Invoice Splitter")
st.write("Upload a PDF and split it into separate invoices based on invoice number.")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    # Open PDF in memory
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    invoice_page_groups = {}
    current_invoice = None

    # Group pages by invoice number
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        invoice_number = extract_invoice_number_by_position(page)
        
        if invoice_number:
            current_invoice = invoice_number
            if current_invoice not in invoice_page_groups:
                invoice_page_groups[current_invoice] = []
        if current_invoice:
            invoice_page_groups[current_invoice].append(page_number)

    st.success(f"Found {len(invoice_page_groups)} invoices.")

    # Create downloads
    for invoice_number, pages in invoice_page_groups.items():
        new_pdf = fitz.open()
        for page_number in pages:
            new_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)
        
        buf = BytesIO()
        new_pdf.save(buf)
        st.download_button(
            label=f"Download {invoice_number}.pdf",
            data=buf.getvalue(),
            file_name=f"{invoice_number}.pdf",
            mime="application/pdf"
        )

    st.info("✅ All invoices are ready to download.")
