"""
Retrieval Agent — Updated
Supports re-retrieval with more chunks when confidence is low.
First attempt: top 5 chunks
Re-retrieval attempt: top 10 chunks + broader query
"""
from app.core.state import AgentState
from app.tools.retrieval_tool import retrieval_tool
from app.core.logger import get_logger

logger = get_logger(__name__)


def retrieval_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Retrieval Agent
    - First run: retrieves top 5 chunks using policy as query
    - Re-retrieval run: retrieves top 10 chunks using both
      policy + document keywords for broader coverage
    """
    is_retry = state.retrieval_attempts > 0
    logger.info(
        f"[RetrievalAgent] Starting — "
        f"attempt={state.retrieval_attempts + 1} retry={is_retry}"
    )

    if state.error:
        logger.warning("[RetrievalAgent] Skipping due to upstream error")
        return state

    try:
        if is_retry:
            # Broader query on re-retrieval: combine policy + first 200 chars of doc
            query = f"{state.policy_text[:300]} {state.document_text[:200]}"
            n_results = 10
            logger.info("[RetrievalAgent] Re-retrieval with broader query + more chunks")
        else:
            # First attempt: policy-focused query
            query = state.policy_text[:500]
            n_results = 5

        chunks = retrieval_tool(
            collection_name=f"task_{state.task_id}",
            query=query,
            n_results=n_results,
        )

        state.retrieved_context = chunks
        state.retrieval_attempts += 1
        state.steps_taken.append(
            f"retrieval_agent: retrieved {len(chunks)} chunks "
            f"(attempt {state.retrieval_attempts})"
        )
        logger.info(
            f"[RetrievalAgent] Done — "
            f"{len(chunks)} chunks retrieved"
        )

    except Exception as e:
        logger.error(f"[RetrievalAgent] Error: {e}")
        state.error = str(e)

    return state