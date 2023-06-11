"""Ingest a PDF or arxiv link."""

import io
from PyPDF2 import PdfReader
import requests
from termcolor import colored


def download_pdf(url: str) -> str:
    """Scrape contents of PDF from a URL."""
    # Download PDF
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    # Use PdfReader to read the PDF
    pdf_content = io.BytesIO(response.content)
    pdf = PdfReader(pdf_content)
    text = ""

    print(colored(f"Number of pages: {len(pdf.pages)}", "green"))
    for page in pdf.pages:
        text += page.extract_text()

    return text


def read_pdf(url: str) -> str:
    """Ingest a PDF or arxiv link."""
    # Check if URL is a PDF. If abs, convert to PDF URL.
    if url.startswith("https://arxiv.org/abs/"):
        # Convert to PDF URL
        url = url.replace("https://arxiv.org/abs/", "https://arxiv.org/pdf/")
        url += ".pdf"

    if url.endswith(".pdf") and url.startswith("https://arxiv.org/pdf/"):
        return download_pdf(url)
    else:
        return ValueError("Invalid URL")
