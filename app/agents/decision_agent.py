"""
Decision Agent
Applies policy rules to the analysis summary.
Returns the final PASS / FAIL / NEEDS_INFO verdict.
"""
from app.core.state import AgentState
from app.tools.decision_tool import decision_tool
from app.core.logger import get_logger

logger = get_logger(__name__)


def decision_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Decision Agent
    - Calls decision_tool with policy + analysis
    - Fills state.decision, reasons, evidence, confidence
    """
    logger.info(f"[DecisionAgent] Starting for task_id={state.task_id}")

    if state.error:
        logger.warning("[DecisionAgent] Skipping due to upstream error")
        state.decision = "NEEDS_INFO"
        state.reasons = [f"Pipeline error: {state.error}"]
        state.evidence = []
        state.confidence = 0.0
        return state

    try:
        result = decision_tool(
            policy_text=state.policy_text,
            analysis_summary=state.analysis_summary,
        )

        state.decision = result.get("decision", "NEEDS_INFO")
        state.reasons = result.get("reasons", [])
        state.evidence = result.get("evidence", [])
        state.confidence = float(result.get("confidence", 0.0))
        state.steps_taken.append(
            f"decision_agent: verdict={state.decision} confidence={state.confidence}"
        )
        logger.info(f"[DecisionAgent] Done — {state.decision}")
    except Exception as e:
        logger.error(f"[DecisionAgent] Error: {e}")
        state.decision = "NEEDS_INFO"
        state.reasons = [f"Decision error: {str(e)}"]
        state.evidence = []
        state.confidence = 0.0

    return state