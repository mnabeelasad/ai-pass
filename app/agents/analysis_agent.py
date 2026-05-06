"""
Analysis Agent — Updated
Now returns an analysis_confidence score so LangGraph
can decide whether to re-retrieve or proceed to decision.
"""
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.state import AgentState
from app.core.config import settings
from app.core.logger import get_logger
from typing import List

logger = get_logger(__name__)

ANALYSIS_SYSTEM_PROMPT = """You are an expert document analyst.
Analyze the given document using the retrieved context and memory of past decisions.

Return ONLY valid JSON with this exact structure:
{
  "summary": "detailed analysis summary here",
  "confidence": 0.0 to 1.0,
  "has_enough_context": true or false
}

confidence rules:
- 0.0 to 0.5: not enough context to make a reliable analysis
- 0.5 to 0.75: moderate context, analysis possible but uncertain
- 0.75 to 1.0: strong context, confident analysis

has_enough_context:
- false if critical information is missing or ambiguous
- true if document has enough detail to evaluate against policy
"""


def analysis_agent(state: AgentState) -> AgentState:
    """
    LangGraph node: Analysis Agent
    - Analyzes document + retrieved context + memory
    - Returns analysis_confidence for conditional routing
    """
    logger.info(f"[AnalysisAgent] Starting — attempt {state.retrieval_attempts + 1}")

    if state.error:
        logger.warning("[AnalysisAgent] Skipping due to upstream error")
        return state

    try:
        context_block = (
            "\n\n---\n\n".join(state.retrieved_context)
            if state.retrieved_context
            else "No context retrieved."
        )

        user_prompt = f"""
Document to analyze:
{state.document_text}

Retrieved context from knowledge base:
{context_block}

Session memory (past decisions):
{state.memory_context if state.memory_context else "No previous decisions."}

Policy being evaluated against:
{state.policy_text[:300]}

Analyze and return JSON.
"""

        llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.2,
        )

        response = llm.invoke([
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)

        state.analysis_summary = parsed.get("summary", "")
        state.analysis_confidence = float(parsed.get("confidence", 0.5))
        state.steps_taken.append(
            f"analysis_agent: confidence={state.analysis_confidence:.2f} "
            f"has_context={parsed.get('has_enough_context', True)}"
        )

        logger.info(
            f"[AnalysisAgent] Done — "
            f"confidence={state.analysis_confidence:.2f}"
        )

    except Exception as e:
        logger.error(f"[AnalysisAgent] Error: {e}")
        # Fallback: use plain text response
        state.analysis_summary = response.content if 'response' in dir() else str(e)
        state.analysis_confidence = 0.4  # low confidence on error → will re-retrieve
        state.error = None  # don't stop pipeline, let conditional handle it

    return state