"""
Orchestrator — LangGraph Multi-Agent Pipeline

Flow:
  ingestion_agent → retrieval_agent → analysis_agent → decision_agent → END
"""
from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.ingestion_agent import ingestion_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.analysis_agent import analysis_agent
from app.agents.decision_agent import decision_agent
from app.core.logger import get_logger

logger = get_logger(__name__)


def build_graph() -> StateGraph:
    """Constructs and compiles the LangGraph agent pipeline."""

    # Use dict-based state for LangGraph compatibility
    def wrap(fn):
        def node(state: dict) -> dict:
            agent_state = AgentState(**state)
            result = fn(agent_state)
            return result.dict()
        return node

    graph = StateGraph(dict)

    # Register nodes
    graph.add_node("ingestion", wrap(ingestion_agent))
    graph.add_node("retrieval", wrap(retrieval_agent))
    graph.add_node("analysis", wrap(analysis_agent))
    graph.add_node("decision", wrap(decision_agent))

    # Define edges (linear pipeline)
    graph.set_entry_point("ingestion")
    graph.add_edge("ingestion", "retrieval")
    graph.add_edge("retrieval", "analysis")
    graph.add_edge("analysis", "decision")
    graph.add_edge("decision", END)

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
        logger.info("LangGraph pipeline compiled and ready")
    return _compiled_graph


def run_pipeline(
    task_id: str,
    document_text: str,
    policy_text: str,
) -> AgentState:
    """
    Entry point: runs the full agent pipeline for a task.

    Returns:
        Final AgentState with decision, reasons, evidence, confidence
    """
    logger.info(f"[Orchestrator] Starting pipeline for task_id={task_id}")

    initial_state = AgentState(
        task_id=task_id,
        document_text=document_text,
        policy_text=policy_text,
    ).dict()

    graph = get_compiled_graph()
    final_state_dict = graph.invoke(initial_state)
    final_state = AgentState(**final_state_dict)

    logger.info(
        f"[Orchestrator] Pipeline complete — "
        f"decision={final_state.decision} | steps={len(final_state.steps_taken)}"
    )
    return final_state