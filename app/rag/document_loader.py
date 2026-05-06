"""
Document Loader
Supports ingestion of PDF, TXT, and DOCX files.
Returns plain text for the RAG pipeline.
"""
import io
from typing import Union
from app.core.logger import get_logger

logger = get_logger(__name__)


def load_txt(file_bytes: bytes) -> str:
    """Load plain text file."""
    text = file_bytes.decode("utf-8", errors="ignore")
    logger.info(f"[DocumentLoader] TXT loaded — {len(text)} chars")
    return text.strip()


def load_pdf(file_bytes: bytes) -> str:
    """Load PDF file using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pages.append(extracted.strip())
        text = "\n\n".join(pages)
        logger.info(f"[DocumentLoader] PDF loaded — {len(reader.pages)} pages, {len(text)} chars")
        return text.strip()
    except ImportError:
        logger.error("[DocumentLoader] pypdf not installed")
        raise RuntimeError("pypdf is required for PDF support. Run: pip install pypdf")


def load_docx(file_bytes: bytes) -> str:
    """Load DOCX file using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        logger.info(f"[DocumentLoader] DOCX loaded — {len(paragraphs)} paragraphs, {len(text)} chars")
        return text.strip()
    except ImportError:
        logger.error("[DocumentLoader] python-docx not installed")
        raise RuntimeError("python-docx is required for DOCX support. Run: pip install python-docx")


def load_document(file_bytes: bytes, filename: str) -> str:
    """
    Auto-detects file type from filename and extracts text.

    Args:
        file_bytes: Raw file bytes
        filename: Original filename (used to detect type)

    Returns:
        Extracted plain text
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".txt"):
        return load_txt(file_bytes)
    elif filename_lower.endswith(".pdf"):
        return load_pdf(file_bytes)
    elif filename_lower.endswith(".docx"):
        return load_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Supported: .txt, .pdf, .docx")