from typing import List
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_embedder():
    """
    Uses OpenAI text-embedding-3-small (Low RAM usage for Render)
    """
    from langchain_openai import OpenAIEmbeddings
    logger.info("Using OpenAI embeddings to save server RAM")
    
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key,
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