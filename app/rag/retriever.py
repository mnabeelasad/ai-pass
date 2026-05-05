from typing import List
from app.rag.vector_store import query_documents
from app.rag.embedder import get_embedder
from app.core.logger import get_logger

logger = get_logger(__name__)

_embedder = None


def get_cached_embedder():
    global _embedder
    if _embedder is None:
        _embedder = get_embedder()
    return _embedder


def retrieve_relevant_context(
    collection_name: str,
    query: str,
    n_results: int = 5,
) -> List[str]:
    """Main retrieval function used by the retrieval agent."""
    embedder = get_cached_embedder()
    chunks = query_documents(
        collection_name=collection_name,
        query=query,
        embedder=embedder,
        n_results=n_results,
    )
    logger.info(f"Retrieved {len(chunks)} chunks for query: '{query[:60]}...'")
    return chunks