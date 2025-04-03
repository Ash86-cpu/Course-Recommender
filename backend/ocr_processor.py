import pdfplumber

def extract_text(pdf_path):
    """Extract text from PDF transcript"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text