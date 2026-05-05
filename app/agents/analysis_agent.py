"""
Analysis Agent
Sends the document + retrieved context to the analysis tool.
Fills state.analysis_summary.
"""
from app.core.state import AgentState
from app.tools.analysis_tool import analysis_tool
from app.core.logger import get_logger

logger = get_logger(__name__)


def analysis_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Analysis Agent
    - Calls analysis_tool with document + retrieved context
    - Fills state.analysis_summary
    """
    logger.info(f"[AnalysisAgent] Starting for task_id={state.task_id}")

    if state.error:
        logger.warning("[AnalysisAgent] Skipping due to upstream error")
        return state

    try:
        summary = analysis_tool(
            document_text=state.document_text,
            retrieved_context=state.retrieved_context,
        )
        state.analysis_summary = summary
        state.steps_taken.append("analysis_agent: document analyzed with RAG context")
        logger.info("[AnalysisAgent] Done")
    except Exception as e:
        logger.error(f"[AnalysisAgent] Error: {e}")
        state.error = str(e)

    return state