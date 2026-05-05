import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_client: chromadb.Client = None


def get_chroma_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB initialized at {settings.chroma_persist_path}")
    return _client


def get_or_create_collection(collection_name: str):
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    logger.info(f"Using ChromaDB collection: {collection_name}")
    return collection


def add_documents(
    collection_name: str,
    chunks: List[str],
    embedder,
    task_id: str,
):
    """Embed and store chunks in ChromaDB."""
    collection = get_or_create_collection(collection_name)

    embeddings = embedder.embed_documents(chunks)
    ids = [f"{task_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"task_id": task_id, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    logger.info(f"Stored {len(chunks)} chunks into collection '{collection_name}'")


def query_documents(
    collection_name: str,
    query: str,
    embedder,
    n_results: int = 5,
) -> List[str]:
    """Retrieve top-k relevant chunks for a query."""
    collection = get_or_create_collection(collection_name)

    query_embedding = embedder.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents"],
    )

    docs = results.get("documents", [[]])[0]
    logger.info(f"Retrieved {len(docs)} chunks from '{collection_name}'")
    return docs