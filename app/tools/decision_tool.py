"""
Tool: DecisionTool
Applies policy rules to the analysis summary and returns
a structured verdict: PASS / FAIL / NEEDS_INFO.
"""
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

DECISION_SYSTEM_PROMPT = """You are a strict policy compliance evaluator.

Given an analysis summary and a set of policy rules, you must:
1. Evaluate whether the document PASSES, FAILS, or NEEDS_INFO
2. Return ONLY valid JSON — no markdown, no explanation outside JSON

Return this exact structure:
{
  "decision": "PASS" | "FAIL" | "NEEDS_INFO",
  "reasons": ["reason 1", "reason 2"],
  "evidence": ["quote or fact from document", ...],
  "confidence": 0.0 to 1.0
}

Rules:
- PASS: Document clearly satisfies all policy requirements
- FAIL: Document violates one or more policy rules
- NEEDS_INFO: Cannot determine due to missing or ambiguous information
"""


def decision_tool(
    policy_text: str,
    analysis_summary: str,
) -> dict:
    """
    Applies policy rules to the analysis and returns a structured verdict.

    Args:
        policy_text: The policy/rules to evaluate against
        analysis_summary: The output from the analysis agent

    Returns:
        dict with decision, reasons, evidence, confidence
    """
    user_prompt = f"""
Policy Rules:
{policy_text}

Document Analysis:
{analysis_summary}

Now evaluate and return the JSON verdict.
"""

    llm = ChatOpenAI(
        model=settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.0,
    )

    logger.info("[DecisionTool] Evaluating against policy")
    response = llm.invoke([
        SystemMessage(content=DECISION_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    raw = response.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"[DecisionTool] Failed to parse JSON: {e}\nRaw: {raw}")
        result = {
            "decision": "NEEDS_INFO",
            "reasons": ["Failed to parse LLM decision output"],
            "evidence": [],
            "confidence": 0.0,
        }

    logger.info(f"[DecisionTool] Decision: {result.get('decision')} | Confidence: {result.get('confidence')}")
    return result