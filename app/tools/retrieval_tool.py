"""
Tool: RetrievalTool
Callable by agents to fetch relevant context from the vector store.
"""
from typing import List
from app.rag.retriever import retrieve_relevant_context
from app.core.logger import get_logger

logger = get_logger(__name__)


def retrieval_tool(collection_name: str, query: str, n_results: int = 5) -> List[str]:
    """
    Retrieves semantically relevant chunks from the vector store.

    Args:
        collection_name: ChromaDB collection to query
        query: The search query (usually from policy or key question)
        n_results: Number of chunks to retrieve

    Returns:
        List of relevant text chunks
    """
    logger.info(f"[RetrievalTool] Query='{query[:60]}' | Collection={collection_name}")
    results = retrieve_relevant_context(
        collection_name=collection_name,
        query=query,
        n_results=n_results,
    )
    logger.info(f"[RetrievalTool] Returned {len(results)} chunks")
    return results