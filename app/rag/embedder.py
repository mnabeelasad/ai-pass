from typing import List
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_embedder():
    """
    Returns the appropriate embedding function.
    - 'local': uses sentence-transformers (free, no API key needed)
    - 'openai': uses OpenAI text-embedding-3-small
    """
    if settings.embedding_mode == "openai":
        from langchain_openai import OpenAIEmbeddings
        logger.info("Using OpenAI embeddings")
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        logger.info("Using local HuggingFace embeddings (all-MiniLM-L6-v2)")
        return HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Simple sliding-window chunker."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    logger.info(f"Chunked text into {len(chunks)} chunks")
    return chunks