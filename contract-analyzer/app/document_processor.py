import os
from pypdf import PdfReader
import docx


class UnsupportedFileType(Exception):
    pass


def extract_text(file_path: str, file_type: str) -> str:
    file_type = file_type.lower()
    if file_type == ".pdf":
        return _extract_pdf(file_path)
    elif file_type == ".docx":
        return _extract_docx(file_path)
    elif file_type == ".txt":
        return _extract_txt(file_path)
    else:
        raise UnsupportedFileType(f"Unsupported file type: {file_type}")


def _extract_pdf(path: str) -> str:
    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def _extract_docx(path: str) -> str:
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs).strip()


def _extract_txt(path: str) -> str:
    with open(path, "r", errors="ignore") as f:
        return f.read().strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """Split text into overlapping chunks for semantic search / long-doc handling."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            break
        if end >= len(words):
            break
    return chunks if chunks else [text]


def validate_file(filename: str, size_bytes: int, max_mb: int, allowed_ext: set) -> tuple:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_ext:
        return False, f"File type '{ext}' not supported. Allowed: {', '.join(allowed_ext)}"
    if size_bytes > max_mb * 1024 * 1024:
        return False, f"File exceeds max size of {max_mb}MB"
    return True, ""
