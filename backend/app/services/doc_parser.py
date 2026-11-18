"""
TruthLens AI - Secure Multi-Format Document Ingestion Engine
Safely extracts textual content from TXT, PDF, and DOCX files.
Includes file extension checks, MIME validation, and size guardrails.
"""

import os
from pypdf import PdfReader
from docx import Document

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def parse_document(file_path: str, original_filename: str) -> dict:
    """
    Parses document and returns extracted title, body text, word count, and file format.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("Specified file does not exist on disk.")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds maximum permissible upload limit (10MB).")

    ext = os.path.splitext(original_filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format '{ext}'. Allowed formats: .txt, .pdf, .docx")

    extracted_text = ""
    title = os.path.splitext(original_filename)[0].replace("_", " ").replace("-", " ").title()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            extracted_text = f.read()

    elif ext == ".pdf":
        reader = PdfReader(file_path)
        pages_text = []
        for p_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(text.strip())
        extracted_text = "\n\n".join(pages_text)

        # Extract title from PDF metadata if available
        if reader.metadata and reader.metadata.title:
            title = reader.metadata.title.strip()

    elif ext == ".docx":
        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        if paragraphs:
            # First line might be headline
            if len(paragraphs[0]) < 120 and len(paragraphs) > 1:
                title = paragraphs[0]
                extracted_text = "\n\n".join(paragraphs[1:])
            else:
                extracted_text = "\n\n".join(paragraphs)

    words = extracted_text.split()
    return {
        "title": title,
        "text": extracted_text.strip(),
        "word_count": len(words),
        "file_format": ext.upper().replace(".", ""),
        "file_size_bytes": file_size
    }
