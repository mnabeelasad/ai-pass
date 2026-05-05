"""
Ingestion Agent
Chunks the input document and stores embeddings in ChromaDB.
"""
from app.core.state import AgentState
from app.rag.embedder import chunk_text, get_embedder
from app.rag.vector_store import add_documents
from app.core.logger import get_logger

logger = get_logger(__name__)

_embedder = None


def get_cached_embedder():
    global _embedder
    if _embedder is None:
        _embedder = get_embedder()
    return _embedder


def ingestion_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Ingestion Agent
    - Chunks document text
    - Embeds and stores in ChromaDB
    """
    logger.info(f"[IngestionAgent] Starting for task_id={state.task_id}")

    try:
        chunks = chunk_text(state.document_text, chunk_size=300, overlap=30)
        state.chunks = chunks

        embedder = get_cached_embedder()
        add_documents(
            collection_name=f"task_{state.task_id}",
            chunks=chunks,
            embedder=embedder,
            task_id=state.task_id,
        )

        state.steps_taken.append("ingestion_agent: document chunked and embedded")
        logger.info(f"[IngestionAgent] Done — {len(chunks)} chunks stored")
    except Exception as e:
        logger.error(f"[IngestionAgent] Error: {e}")
        state.error = str(e)

    return state