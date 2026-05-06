"""
Orchestrator — Advanced LangGraph Pipeline

Flow with conditional branching:

  ingestion
      │
  retrieval (attempt 1)
      │
  analysis
      │
  [confidence_router] ←── NEW conditional node
     ↙           ↘
  low (<0.6)    high (>=0.6)
     ↓               ↓
  retrieval       decision
  (attempt 2)         │
     ↓              END
  analysis
     ↓
  decision
     │
    END
"""
from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.ingestion_agent import ingestion_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.analysis_agent import analysis_agent
from app.agents.decision_agent import decision_agent
from app.core.logger import get_logger

logger = get_logger(__name__)

# Confidence threshold — below this we re-retrieve
CONFIDENCE_THRESHOLD = 0.6
# Max re-retrieval attempts to avoid infinite loops
MAX_RETRIEVAL_ATTEMPTS = 2


def wrap(fn):
    """Wraps AgentState-based functions for LangGraph dict-based state."""
    def node(state: dict) -> dict:
        agent_state = AgentState(**state)
        result = fn(agent_state)
        return result.dict()
    return node


def confidence_router(state: dict) -> str:
    """
    Conditional edge function.
    Routes to 're_retrieval' if confidence is low,
    otherwise routes to 'decision'.
    """
    confidence = state.get("analysis_confidence", 0.0)
    attempts = state.get("retrieval_attempts", 0)
    error = state.get("error")

    if error:
        logger.info(f"[Router] Error detected → routing to decision")
        return "decision"

    if confidence < CONFIDENCE_THRESHOLD and attempts < MAX_RETRIEVAL_ATTEMPTS:
        logger.info(
            f"[Router] Low confidence ({confidence:.2f}) → "
            f"re-retrieving (attempt {attempts + 1})"
        )
        return "re_retrieval"

    logger.info(
        f"[Router] Confidence OK ({confidence:.2f}) → "
        f"proceeding to decision"
    )
    return "decision"


def build_graph() -> StateGraph:
    """Constructs and compiles the advanced LangGraph pipeline."""

    graph = StateGraph(dict)

    # ── Register nodes ─────────────────────────────────────────
    graph.add_node("ingestion",    wrap(ingestion_agent))
    graph.add_node("retrieval",    wrap(retrieval_agent))
    graph.add_node("analysis",     wrap(analysis_agent))
    graph.add_node("re_retrieval", wrap(retrieval_agent))   # same fn, retry mode
    graph.add_node("re_analysis",  wrap(analysis_agent))    # re-analyze after retry
    graph.add_node("decision",     wrap(decision_agent))

    # ── Linear edges ───────────────────────────────────────────
    graph.set_entry_point("ingestion")
    graph.add_edge("ingestion",    "retrieval")
    graph.add_edge("retrieval",    "analysis")

    # ── Conditional edge after analysis ────────────────────────
    graph.add_conditional_edges(
        "analysis",
        confidence_router,
        {
            "re_retrieval": "re_retrieval",
            "decision":     "decision",
        }
    )

    # ── Re-retrieval path ──────────────────────────────────────
    graph.add_edge("re_retrieval", "re_analysis")

    # ── After re-analysis always go to decision ────────────────
    graph.add_edge("re_analysis",  "decision")
    graph.add_edge("decision",     END)

    return graph.compile()


# Singleton
_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
        logger.info("Advanced LangGraph pipeline compiled")
    return _compiled_graph


def run_pipeline(
    task_id: str,
    document_text: str,
    policy_text: str,
    session_id: str = "default",
) -> AgentState:
    """
    Runs the full advanced agent pipeline.
    Accepts optional session_id for memory context.
    """
    from app.storage.memory_store import get_memory_summary

    logger.info(
        f"[Orchestrator] Starting pipeline — "
        f"task={task_id} session={session_id}"
    )

    # Inject memory context from past decisions
    memory_context = get_memory_summary(session_id)
    logger.info(f"[Orchestrator] Memory context: {memory_context[:100]}")

    initial_state = AgentState(
        task_id=task_id,
        document_text=document_text,
        policy_text=policy_text,
        session_id=session_id,
        memory_context=memory_context,
    ).dict()

    graph = get_compiled_graph()
    final_state_dict = graph.invoke(initial_state)
    final_state = AgentState(**final_state_dict)

    # Save result to memory for future tasks in same session
    from app.storage.memory_store import save_to_memory
    if final_state.decision:
        save_to_memory(
            session_id=session_id,
            task_id=task_id,
            decision=final_state.decision,
            reasons=final_state.reasons,
            evidence=final_state.evidence,
            confidence=final_state.confidence,
            document_preview=document_text[:200],
        )

    logger.info(
        f"[Orchestrator] Pipeline complete — "
        f"decision={final_state.decision} | "
        f"steps={len(final_state.steps_taken)} | "
        f"retrieval_attempts={final_state.retrieval_attempts}"
    )
    return final_state