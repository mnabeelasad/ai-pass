"""
Retrieval Agent
Queries the vector store using the policy text as a query.
Injects retrieved context into the shared state.
"""
from app.core.state import AgentState
from app.tools.retrieval_tool import retrieval_tool
from app.core.logger import get_logger

logger = get_logger(__name__)


def retrieval_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Retrieval Agent
    - Uses policy text as the retrieval query
    - Fills state.retrieved_context
    """
    logger.info(f"[RetrievalAgent] Starting for task_id={state.task_id}")

    if state.error:
        logger.warning("[RetrievalAgent] Skipping due to upstream error")
        return state

    try:
        # Use policy text as the retrieval query to find policy-relevant chunks
        query = state.policy_text[:500]  # Use first 500 chars as query

        chunks = retrieval_tool(
            collection_name=f"task_{state.task_id}",
            query=query,
            n_results=5,
        )
        state.retrieved_context = chunks
        state.steps_taken.append(
            f"retrieval_agent: retrieved {len(chunks)} relevant chunks"
        )
        logger.info(f"[RetrievalAgent] Done — {len(chunks)} chunks retrieved")
    except Exception as e:
        logger.error(f"[RetrievalAgent] Error: {e}")
        state.error = str(e)

    return state